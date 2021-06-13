import torch
import os

import resources.utils.models as models

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def load_model(model_path, input_channels=4, num_classes=1):
    """
    Carga en GPU un modelo de PyTorch.

    :param model_path: archivo .pth que representa al modelo
    :type model_path: str

    :param input_channels: bandas de la imagen de entrada
    :type input_channels: int

    :param num_classes: cantidad de clases de predicción
    :type num_classes: int

    :rtype: torch.nn.Module
    """
    print(os.system("pwd"))
    model = models.UNet11(num_classes=num_classes, input_channels=input_channels)
    model.load_state_dict(torch.load(model_path))
    model.to(device)
    return model


def run_model(patch, model):
    """
    Ejecuta un modelo de PyTorch.

    :param patch: imagen a procesar;
    :type patch: torch.autograd.Variable

    :param model: modelo de PyTorch
    :type model: torch.nn.Module
    """
    model.eval()
    # print("Model in eval mode")
    with torch.set_grad_enabled(False):
        response = torch.sigmoid(model(patch))
    return response


def run_model_softmax(patch, model):
    """
    Ejecuta un modelo de PyTorch.

    :param patch: imagen a procesar;
    :type patch: torch.autograd.Variable

    :param model: modelo de PyTorch
    :type model: torch.nn.Module
    """
    model.eval()
    # print("Model in eval mode")
    with torch.set_grad_enabled(False):
        response = torch.exp(model(patch))
    return response
