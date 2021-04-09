from flask import Blueprint
from flask_restful import Api

# Importing Resources from resources/
from resources.checkfiles import CheckFileResource
from resources.predict import PredictResource
from resources.searchImages import SearchImagesResource

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

api.add_resource(PredictResource, '/predict/')
api.add_resource(CheckFileResource, '/checkFiles/')
api.add_resource(SearchImagesResource, '/searchImages/')
