from os import listdir
from os.path import join, dirname, realpath

from flask import request
from flask_restful import Resource

import status
from resources.utils.image_utils import get_bounding_box_from_name
from resources.utils.json_utils import build_response_from_search

UPLOAD_DIRECTORY = join(dirname(realpath(__file__)), '../static/')


class CheckFileResource(Resource):
    def get(self):
        """Verifica si existe una máscara ya procesada y almacenada con el nombre brindado."""

        if 'name' not in request.args:
            response = {'error': 'No filename given'}
            return response, status.HTTP_400_BAD_REQUEST

        last_slash = request.args['name'].rfind('/') + 1  # Ocurrencia de la última diagonal + 1
        last_dot = request.args['name'].rfind('.')  # Ocurrencia del último punto
        image_name = request.args['name'][last_slash:last_dot]  # Nombre de la imagen

        tif_filename = image_name + '_MASK.TIF'
        png_filename = image_name + '_MASK.png'
        png_raster_filename = image_name + '.JPG'
        # Como las máscaras se almadenan con el sufijo _MASK, de existir la máscara ya procesada, estaría con el
        # nombre original + el sufijo

        preprocessed_masks = listdir(UPLOAD_DIRECTORY)

        is_located = (tif_filename in preprocessed_masks) and (png_filename in preprocessed_masks) and\
                     (png_raster_filename in preprocessed_masks)

        if not is_located:
            print("Archivo no encontrado.")
            return build_response_from_search(is_located, tif_filename, png_filename, png_raster_filename, {})

        bounding_box = get_bounding_box_from_name(UPLOAD_DIRECTORY + tif_filename)

        response = build_response_from_search(is_located, tif_filename, png_filename, png_raster_filename, bounding_box)

        return response, status.HTTP_200_OK
