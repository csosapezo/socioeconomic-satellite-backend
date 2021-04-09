import os
import time
from io import BytesIO

import numpy as np
import progressbar
import rasterio
from flask import request
from flask_restful import Resource
from rasterio.io import MemoryFile
import pysftp

import status
from resources.utils.image_utils import create_patches, reconstruct_image, convert_mask_to_png, convert_raster_to_png,\
    get_bounding_box, get_png_raster
from resources.utils.json_utils import build_response
from resources.utils.segmenter import WaterSegmentation
from secret_config.credentials import *

UPLOAD_DIRECTORY = "static/"
MODEL_PATH = 'models/model_40epoch_100_percent_UNet11_fold0.pth'

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

model = WaterSegmentation(MODEL_PATH)


class PredictResource(Resource):
    def post(self):
        """Recurso RESTful que devuelve una máscara que señala los cuerpos de agua presentes en una imagen satelital
        de cuatro bandas. Este recurso requiere recibir, además de la imagen, el nombre de la misma para asignarle a
        la máscara uno derivado de esta.

        Argumentos:
        file:     imagen satelital de cuatro bandas y de cuatro bandas;
        filename: nombre de archivo de la imagen satelital
        """

        start = time.time()
        print("Recibiendo imagen...")
        request_dict = request.get_json()
        if not request_dict:
            response = {'error': 'No data provided'}
            return response, status.HTTP_400_BAD_REQUEST

        filepath = request_dict["filepath"]

        if filepath is None:
            response = {'error': 'No filepath given'}
            return response, status.HTTP_400_BAD_REQUEST

        last_slash = filepath.rfind('/') + 1  # Ocurrencia de la última diagonal + 1
        last_dot = filepath.rfind('.')  # Ocurrencia del último punto
        filename = filepath[last_slash:last_dot]  # Nombre de la imagen

        with pysftp.Connection(host=sftp_hostname, username=sftp_username, password=sftp_password) as sftp:
            print("Nombre del archivo: {}".format(filename))
            file = BytesIO()
            print(filepath)
            sftp.getfo(filepath, file)
            file.seek(0)
            data = file.read()
            reading = time.time()
            print("Imagen recibida, tiempo transcurrido: {}s".format(str(round(reading - start, 2))))
            print("Abriendo la imagen...")

            try:  # Intenta abrir la imagen. De no ser una imagen, se informa al cliente
                memfile = MemoryFile(data)
                dataset = memfile.open()
                profile = dataset.profile
                img_npy = dataset.read()
            except rasterio.errors.RasterioIOError:
                response = {'error': 'File is not an image'}
                return response, status.HTTP_400_BAD_REQUEST

            opening = time.time()
            print("Imagen abierta, tiempo transcurrido: {}s".format(str(round(opening - reading, 2))))

            if img_npy.shape[0] != 4:
                response = {'error': 'Incorrect number of channels'}
                return response, status.HTTP_400_BAD_REQUEST
            elif (img_npy.shape[1] < 512) or (img_npy.shape[2] < 512):
                response = {'error': 'Image can not be split into 4x512x512 patches'}
                return response, status.HTTP_400_BAD_REQUEST

            print("Dimensiones de la imagen: {}".format(str(img_npy.shape)))
            print("Minimo: {} | Maximo: {}".format(str(img_npy.min()), str(img_npy.max())))

            print("Creando bloques de 4 x 512 x 512...")
            patches, meta = create_patches(dataset)
            splitting = time.time()
            print("Bloques de 4 x 512 x 512 creados, tiempo transcurrido: {}s".format(str(round(splitting - opening, 2))))
            masks = []
            bar = progressbar.ProgressBar(maxval=len(patches),
                                        widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Counter(), " / ",
                                                str(len(patches))])
            # La barra se muestra así [=========         ] X / Total
            bar.start()
            idx = 0
            print("Obteniendo las máscaras por cada bloque...")
            for patch in patches:
                prediction = model.predict(patch)
                masks.append(prediction.data.cpu().numpy())
                print(len(masks))
                bar.update(idx + 1)
                idx += 1

            predicting = time.time()
            print("Mascaras obtenidas! Tiempo transcurrido: {}s".format(str(round(predicting - splitting, 2))))
            masks = np.asarray(masks)

            print("Construyendo la mascara final + metadata...")
            print("Nombre de archivo: {}".format(filename))
            mask_filename, mask, mask_metadata = reconstruct_image(masks, meta, img_npy.shape, filename)
            constructing = time.time()
            print("Mascara construida! Tiempo transcurrido: {}s".format(str(round(constructing - predicting, 2))))

            print("Convirtiendo máscara a PNG...")
            png_filename = convert_mask_to_png(mask_filename, mask, mask_metadata)
            raster_png_filename = get_png_raster(filepath, sftp, mask_metadata)
            converting = time.time()
            print("Conversión exitosa! Tiempo transcurrido: {}s".format(str(round(converting - constructing, 2))))

            bounding_box = get_bounding_box(memfile.open())

            end = time.time()
            response = build_response(mask_filename, png_filename, raster_png_filename, bounding_box)
            print("Tiempo total: {}s".format(str(round(end - start, 2))))

            return response, status.HTTP_200_OK
