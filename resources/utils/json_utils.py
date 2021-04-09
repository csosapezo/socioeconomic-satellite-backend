import dateutil.parser
from flask import url_for


def build_response(tif_filename, png_filename, raster_png_filename, bounding_box):
    """Prepara los datos a enviar en un diccionario entendible por el solicitante

    :param tif_filename: cadena con la ruta a la imagen en tif
    :type tif_filename: str

    :param png_filename: cadena con la ruta a la imagen en png
    :type png_filename: str

    :param raster_png_filename: cadena con la ruta a la imagen original en png
    :type raster_png_filename: str

    :param bounding_box: diccionario de coordenadas
    :type bounding_box: dict
    """
    return {
        "mask": {
            'tif_filename': url_for('static', filename=tif_filename),
            'png_mask': url_for('static', filename=png_filename),
            'png_raster': url_for('static', filename=raster_png_filename),
            'bounding_box': {
                'top': bounding_box['top'],
                'bottom': bounding_box['bottom'],
                'left': bounding_box['left'],
                'right': bounding_box['right']
            }
        }
    }


def build_response_from_search(is_located, tif_filename, png_filename, raster_png_filename, bounding_box):
    """Prepara los datos a enviar en un diccionario entendible por el solicitante

    :param is_located: variable lógica que es verdader si se encontró el archivo
    :type is_located: bool

    :param tif_filename: cadena con la ruta a la imagen en tif
    :type tif_filename: str

    :param png_filename: cadena con la ruta a la imagen en png
    :type png_filename: str

    :param raster_png_filename: cadena con la ruta a la imagen original en png
    :type raster_png_filename: str

    :param bounding_box: diccionario de coordenadas
    :type bounding_box: dict
    """
    if is_located:
        return {
            "is_located": is_located,
            "mask": {
                'tif_filename': url_for('static', filename=tif_filename),
                'png_mask': url_for('static', filename=png_filename),
                'png_raster': url_for('static', filename=raster_png_filename),
                'bounding_box': {
                    'top': bounding_box['top'],
                    'bottom': bounding_box['bottom'],
                    'left': bounding_box['left'],
                    'right': bounding_box['right']
                }
            }
        }
    else:
        return {
            "is_located": is_located,
            "mask": {}
        }


def read_search_data(json_data):
    """Lee una petición de búsqueda de imágenes satelitales.

    :param json_data: datos en formato JSON con la fecha de inicio, la fecha de fin y las coordenadas de búsqued
    :type json_data: dict
    """
    start_date = dateutil.parser.parse(json_data["start_date"])
    end_date = dateutil.parser.parse(json_data["end_date"])

    return start_date, end_date, json_data["bounding_box"]
