from io import BytesIO

import pysftp
from flask import request
from flask_restful import Resource
from config.credentials import Credentials

import status
from resources.utils.image_utils import get_bounding_box_from_xml, rect_overlap


class SearchImagesResource(Resource):
    def post(self):
        request_dict = request.get_json()
        if not request_dict:
            error = {'error': 'No data provided.'}
            return error, status.HTTP_400_BAD_REQUEST

        # Los datos de fechas llegaran como fechaini, fechafin ->
        # Los datos de coordenadas llegaran como Norte, Oeste, Sur, Este
        # Top, left, bottom, right

        print(request_dict)

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

            cred = Credentials()

            with pysftp.Connection(host=cred.sftp_hostname,
                                   username=cred.sftp_username,
                                   password=cred.sftp_password) as sftp:
                command = "find ./ternaus -name '*MS*.TIF*'"
                paths = sftp.execute(command)

                date_filtered_paths = []

                for path in paths:
                    path = path[:-1].decode()
                    print(path)

                for (path, date) in date_filtered_paths:
                    file = BytesIO()
                    xml_path = path[:]
                    print(xml_path)

                    # Change path to xml file
                    pos = xml_path.rfind("IMG")
                    xml_path = xml_path[0:pos] + "DIM" + xml_path[pos+3:]
                    xml_path = xml_path[:-3] + "XML"

                    sftp.getfo(xml_path, file)
                    file.seek(0)

                    date = date[6:8] + "/" + date[4:6] + "/" + date[0:4]
                    bounding_box = get_bounding_box_from_xml(file)
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
                            "date": date,
                            "bounding_box": bounding_box
                        })

            return response, status.HTTP_200_OK
        except Exception as e:
            response = {'error': str(e)}
            return response, status.HTTP_400_BAD_REQUEST
