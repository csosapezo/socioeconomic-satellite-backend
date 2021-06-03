import logging
import os
import time
from io import BytesIO

import pysftp
import rasterio
from flask import request
from flask_restful import Resource
from rasterio.io import MemoryFile

import status
from config import SFTPCredentials, ModelPaths
from resources.utils.determinator import IncomeDetermination
from resources.utils.image_utils import get_bounding_box
from resources.utils.json_utils import build_response

UPLOAD_DIRECTORY = "static/"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

paths = ModelPaths()
model = IncomeDetermination(paths)

logger = logging.getLogger('root')
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.DEBUG)


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
        logger.debug("Receiving image...")
        request_dict = request.get_json()
        if not request_dict:
            response = {'error': 'No data provided'}
            logger.error("No data provided!")
            return response, status.HTTP_400_BAD_REQUEST

        filepath = request_dict["filepath"]

        if filepath is None:
            response = {'error': 'No filepath given'}
            logger.error("No filepath given!")
            return response, status.HTTP_400_BAD_REQUEST

        last_slash = filepath.rfind('/') + 1  # Ocurrencia de la última diagonal + 1
        last_dot = filepath.rfind('.')  # Ocurrencia del último punto
        filename = filepath[last_slash:last_dot]  # Nombre de la imagen

        cred = SFTPCredentials()

        with pysftp.Connection(host=cred.sftp_hostname,
                               username=cred.sftp_username,
                               password=cred.sftp_password) as sftp:
            logger.debug("Filename: {}".format(filename))
            file = BytesIO()
            logger.debug(filepath)
            sftp.getfo(filepath, file)
            file.seek(0)
            data = file.read()
            reading = time.time()
            logger.debug("Image Received. Elapsed time: {}s".format(str(round(reading - start, 2))))
            logger.debug("Opening image...")

            try:  # Intenta abrir la imagen. De no ser una imagen, se informa al cliente
                memfile = MemoryFile(data)
                dataset = memfile.open()
                img_npy = dataset.read()
            except rasterio.errors.RasterioIOError:
                response = {'error': 'File is not an image'}
                logger.error("File {} is not an image!".format(filepath))
                return response, status.HTTP_400_BAD_REQUEST

            opening = time.time()
            logger.debug("Image opened. Elapsed time: {}s".format(str(round(opening - reading, 2))))

            if img_npy.shape[0] != 4:
                response = {'error': 'Incorrect number of channels'}
                return response, status.HTTP_400_BAD_REQUEST
            elif (img_npy.shape[1] < 512) or (img_npy.shape[2] < 512):
                response = {'error': 'Image can not be split into 4x512x512 patches'}
                logger.error("Image can not be split into 4x512x512 patches")
                return response, status.HTTP_400_BAD_REQUEST

            logger.debug("Image shape: {}".format(str(img_npy.shape)))

            logger.debug("Generating mask...")

            predict = model.predict(img_npy)

            predicting = time.time()
            logger.debug("Mask generated! Elapsed time: {}s".format(str(round(predicting - opening, 2))))

            bounding_box = get_bounding_box(memfile.open())

            end = time.time()
            response = build_response(bounding_box, predict)
            logger.debug("Total Elapsed Time: {}s".format(str(round(end - start, 2))))

            return response, status.HTTP_200_OK
