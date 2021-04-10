import resources.utils.model_utils as model_utils

from resources.utils.image_utils import preprocess_image


class IncomeDetermination(object):
    def __init__(self, paths):
        self.roof_model = model_utils.load_model(paths.roof_segmentation_model_path)
        self.income_model = model_utils.load_model(paths.income_level_determination_model_path)

    def image_loader(self, img):
        """
        Preprocesa una imagen para ser apta para entrar en el modelo de segmentación.
        """
        img = preprocess_image(img)
        return img

    def predict(self, image):
        """
        Procesa una imagen satelital, previamente preprocesada, mediante un modelo de segmentación y devuelve una
        máscara que señala los cuerpos de agua de la imagen original.
        """

        img_input = self.image_loader(image)
        trained_model = self.roof_model
        response = model_utils.run_model(img_input, trained_model)
        del trained_model
        # TODO add income model steps
        return response
