from os import listdir
from os.path import join, dirname, realpath

from flask import request
from flask_restful import Resource

import status
from resources.utils.image_utils import get_bounding_box_from_name
from resources.utils.json_utils import build_response

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

        preprocessed_masks = listdir(UPLOAD_DIRECTORY)

        response_masks = list(filter(lambda filename: image_name in filename, preprocessed_masks))

        if not response_masks:
            print("Archivo no encontrado.")
            return build_response({}, [], bool(response_masks))

        bounding_box = get_bounding_box_from_name(UPLOAD_DIRECTORY + response_masks[0])

        response = build_response(bounding_box, response_masks, bool(response_masks))

        return response, status.HTTP_200_OK
