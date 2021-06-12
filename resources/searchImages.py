from io import BytesIO

import pysftp
from flask import request
from flask_restful import Resource
from config.sftp_credentials import SFTPCredentials

import status
from resources.utils.image_utils import get_bounding_box_from_file, rect_overlap


class SearchImagesResource(Resource):
    def post(self):
        request_dict = request.get_json()
        if not request_dict:
            error = {'error': 'No data provided.'}
            return error, status.HTTP_400_BAD_REQUEST

        # Los datos de fechas llegaran como fechaini, fechafin ->
        # Los datos de coordenadas llegaran como Norte, Oeste, Sur, Este
        # Top, left, bottom, right

        try:
            left = request_dict["left"]
            bottom = request_dict["bottom"]
            right = request_dict["right"]
            top = request_dict["top"]

            area_of_interest = {
                "left": left,
                "bottom": bottom,
                "right": right,
                "top": top
            }

            response = {
                "images": []
            }

            cred = SFTPCredentials()

            print(cred.sftp_hostname, cred.sftp_username, cred.sftp_password)

            with pysftp.Connection(host=cred.sftp_hostname,
                                   username=cred.sftp_username,
                                   password=cred.sftp_password) as sftp:
                print("conexion exitosa")
                command = "find ./images -name '*P*.tif'"
                paths = sftp.execute(command)

                for path in paths:

                    path = path.decode()
                    print(path)

                    file = BytesIO()

                    sftp.getfo(path, file)
                    file.seek(0)

                    bounding_box = get_bounding_box_from_file(file)
                    print(bounding_box)

                    if (rect_overlap((bounding_box["top"], bounding_box["left"]),
                                     (bounding_box["bottom"], bounding_box["right"]),
                                     (area_of_interest["bottom"], area_of_interest["left"]),
                                     (area_of_interest["top"], area_of_interest["right"]))):
                        last_slash = path.rfind('/') + 1  # Ocurrencia de la última diagonal + 1
                        last_dot = path.rfind('.')  # Ocurrencia del último punto
                        filename = path[last_slash:last_dot]  # Nombre de la imagen
                        response["images"].append({
                            "path": path,
                            "name": filename,
                            "bounding_box": bounding_box
                        })

            return response, status.HTTP_200_OK
        except Exception as e:
            response = {'error': str(e)}
            return response, status.HTTP_400_BAD_REQUEST
