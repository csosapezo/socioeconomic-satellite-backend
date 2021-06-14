import numpy as np
import torch

import resources.utils.model_utils as model_utils

from resources.utils.image_utils import preprocess_image


class IncomeDetermination(object):
    def __init__(self, paths, num_classes):
        self.roof_model = model_utils.load_model(paths.roof_model_state_dict)
        self.income_model = model_utils.load_model(paths.income_model_state_dict, num_classes=num_classes,
                                                   input_channels=5)

    def image_loader(self, img, dataset):
        """
        Preprocesa una imagen para ser apta para entrar en el modelo de segmentación.
        """
        img = preprocess_image(img, dataset)
        return img

    def predict(self, image):
        """
        Procesa una imagen satelital, previamente preprocesada, mediante un modelo de segmentación y devuelve una
        máscara que señala los cuerpos de agua de la imagen original.
        """

        img_input = self.image_loader(image, "roof")
        trained_model = self.roof_model
        roof_response = model_utils.run_model(img_input, trained_model)
        del trained_model

        img_mask_input = np.concatenate((image, roof_response.cpu().numpy()[0]))
        img_mask_input = self.image_loader(img_mask_input, "income")

        trained_model = self.income_model
        response = model_utils.run_model_softmax(img_mask_input, trained_model)
        del trained_model

        return response.cpu().numpy(), roof_response.cpu().numpy()
