import dateutil.parser
from flask import url_for


def build_response(bounding_box, masks, is_located=None):
    """Prepara los datos a enviar en un diccionario entendible por el solicitante

    :param bounding_box: diccionario de coordenadas
    :type bounding_box: dict

    :param masks: lista de direcciones de máscaras
    :type masks: list

    :param is_located: describe si la imagen fue encontrada o no
    :type is_located: bool
    """

    print("mascaras:", masks)

    if is_located is False:
        image = {}
    else:
        image = {

            'bounding_box': {
                'top': bounding_box['top'],
                'bottom': bounding_box['bottom'],
                'left': bounding_box['left'],
                'right': bounding_box['right']
            },

            'masks': [
                {
                    'url': url_for('static', filename=mask),
                    'level': mask[mask.rfind['_'] + 1:mask.rfind['.']]
                }
                for mask in masks]
        }

    return {
        "is_located": is_located if is_located is not None else '',
        "image": image
    }


def read_search_data(json_data):
    """Lee una petición de búsqueda de imágenes satelitales.

    :param json_data: datos en formato JSON con la fecha de inicio, la fecha de fin y las coordenadas de búsqued
    :type json_data: dict
    """
    start_date = dateutil.parser.parse(json_data["start_date"])
    end_date = dateutil.parser.parse(json_data["end_date"])

    return start_date, end_date, json_data["bounding_box"]
