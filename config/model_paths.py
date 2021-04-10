import os

from dotenv import load_dotenv


class ModelPath:
    def __init__(self):
        load_dotenv()
        self.roof_segmentation_model_path = os.getenv("ROOF_SEGMENTATION_MODEL_PATH")
        self.income_level_determination_model_path = os.getenv("INCOME_LEVEL_DETERMINATION_MODEL_PATH")
