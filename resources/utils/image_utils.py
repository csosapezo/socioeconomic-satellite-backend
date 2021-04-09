import os
from itertools import product

import numpy as np
import rasterio as rio
import torch
from pyproj import Transformer
from rasterio import windows
from rasterio.io import MemoryFile
from torch.autograd import Variable
from io import BytesIO

from resources.utils.dataset import to_float_tensor
from resources.utils.transformsdata import CenterCrop, DualCompose, ImageOnly, Normalize
from PIL import Image

from xml.dom import minidom

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
UPLOAD_DIRECTORY = "static/"


def transform_function():
    """Función de normalización para una imagen satelital."""
    image_transform = DualCompose([CenterCrop(512), ImageOnly(
        Normalize(mean=[0.11555246, 0.10432396, 0.1150794, 0.14246734],
                  std=[0.08946183, 0.06699049, 0.05742599, 0.11001556]))])
    return image_transform


def preprocess_image(img):
    """Normaliza y transforma la imagen en un tensor apto para ser procesado por la red neuronal de segmentación de
    cuerpos de agua.
    Dimensiones: entrada: (4,512,512); salida: (1,4,512,512)

    :param img: imagen por preprocesar
    :type img: np.ndarray
    """
    img = img.transpose((1, 2, 0))
    image_transform = transform_function()
    img_for_model = image_transform(img)[0]
    img_for_model = Variable(to_float_tensor(img_for_model), requires_grad=False)
    img_for_model = img_for_model.unsqueeze(0).to(device)

    return img_for_model


def create_patches(dataset):
    """Genera bloques de (4,512,512) píxeles a partir de una imagen satelital.

    :param dataset: lector de conjunto de datos ráster
    :type dataset: rio.DatasetReader
    """
    patches = []

    def get_tiles(ds, width=512, height=512):
        nols, nrows = ds.meta['width'], ds.meta['height']
        offsets = product(range(0, nols, width), range(0, nrows, height))
        big_window = windows.Window(col_off=0, row_off=0, width=nols, height=nrows)

        for col_off, row_off in offsets:
            tile_window = windows.Window(col_off=col_off, row_off=row_off, width=width, height=height).intersection(
                big_window)
            tile_transform = windows.transform(tile_window, ds.transform)  # split

            yield tile_window, tile_transform

    with dataset as inds:
        tile_width, tile_height = 512, 512
        meta = inds.meta.copy()

        for window, transform in get_tiles(inds):
            if (int(window.width) == tile_width) and (int(window.height) == tile_height):
                array = inds.read(window=window)
                patches.append(array)
    return patches, meta


def reconstruct_image(masks, metadata, img_shape, filename):
    """Combina un conjunto de bloques de (1,4,512,512) píxeles para generar una máscara de segmentación de cuerpos de
    agua y guarda el resultado localmente.

    :param masks: lista de máscaras - arrays -  de (1,4,512,512) píxeles;
    :type masks: np.ndarra

    :param metadata: diccionario con los metadatos de la imagen satelital original;
    :type metadata: dict

    :param img_shape: dimensiones de la imagen satelital original;
    :type img_shape: tuple

    :param filename: nombre del archivo que contenía a la imagen original
    :type filename: str
    """
    pos = 0
    # C, H, W
    mask = np.zeros(shape=(1, img_shape[1], img_shape[2]))
    # rows = floor(H / 512), cols = floor(W / 512)

    for j in range(img_shape[2] // 512):
        for i in range(img_shape[1] // 512):
            cur_mask = masks[pos, 0, :, :, :]
            for k in range(512):
                for l in range(512):
                    mask[0, i * 512 + k, j * 512 + l] = cur_mask[0, k, l]
            pos += 1

    h, w = mask.shape[1], mask.shape[2]
    binary_mask = np.zeros(shape=mask.shape, dtype=np.uint8)
    for y in range(mask.shape[1]):
        for x in range(mask.shape[2]):
            binary_mask[0, y, x] = (mask[0, y, x] > 0.5)
    mask = binary_mask

    metadata['count'] = 1
    metadata['height'] = mask.shape[1]
    metadata['width'] = mask.shape[2]
    metadata['dtype'] = mask.dtype
    mask_filename = filename + "_MASK.TIF"
    with rio.open(os.path.join(UPLOAD_DIRECTORY, mask_filename), 'w', **metadata) as outds:
        outds.write(mask)

    return mask_filename, mask, metadata


def convert_mask_to_png(filename, raster, metadata):
    """Transforma una máscara en una imagen png para su visualización en plataformas web.

    :param filename: ruta de la máscara originalmente generada como TIF
    :type filename: str


    :param raster: matriz bidimensional con los valores de la máscara
    :type raster: np.ndarray


    :param metadata: diccionario con los metadatos de la máscara
    :type metadata: dict

    """
    new_metadata = metadata
    new_metadata['count'] = 3
    new_metadata['driver'] = 'PNG'

    png_filename = filename[:-4] + ".png"

    new_raster = np.zeros(shape=[3, new_metadata['height'], new_metadata['width']])
    new_raster[2] = raster[0]
    new_raster[2] = new_raster[2] * 255
    new_raster = new_raster.astype('uint8')

    with rio.open(UPLOAD_DIRECTORY + png_filename, 'w', **new_metadata) as dst:
        dst.write(new_raster)

    return png_filename


def convert_raster_to_png(filename, raster, metadata):
    """Transforma una imagen satelital en una imagen png para su visualización en plataformas web.

    :param filename: ruta del raster original
    :type filename: str


    :param raster: matriz bidimensional con los valores del raster
    :type raster: np.ndarray


    :param metadata: diccionario con los metadatos del raster
    :type metadata: dict

    """
    new_metadata = metadata
    new_metadata['count'] = 3
    new_metadata['driver'] = 'PNG'
    new_metadata['dtype'] = 'uint8'

    png_filename = filename[:-4] + ".png"
    raster = raster[:3]
    new_raster = (raster / raster.max() * 255).astype('uint8')

    with rio.open(UPLOAD_DIRECTORY + png_filename, 'w', **new_metadata) as dst:
        dst.write(new_raster)

    return png_filename

def get_png_raster(filepath, sftp, metadata):
    last_slash = filepath.rfind('/') + 1  # Ocurrencia de la última diagonal + 1
    last_dot = filepath.rfind('.')  # Ocurrencia del último punto
    filename = filepath[last_slash:last_dot]  # Nombre de la imagen

    last_slash = filepath.rfind('/') + 1  # Ocurrencia de la última diagonal + 1
    last_dot = filepath.rfind('.')  # Ocurrencia del último punto
    filepath = filepath[:last_slash] + "PREVIEW" + filepath[last_slash + 3: last_dot] + ".JPG"

    print(filepath)
    file = BytesIO()
    sftp.getfo(filepath, file)
    file.seek(0)
    pic = np.array(Image.open(file))

    pic = pic.transpose((2,0,1))

    new_metadata = metadata
    new_metadata['count'] = 3
    new_metadata['driver'] = 'PNG'
    new_metadata['dtype'] = 'uint8'

    png_filename = filename + ".JPG"

    with rio.open(UPLOAD_DIRECTORY + png_filename, 'w', **new_metadata) as dst:
        dst.write(pic)

    return png_filename



def get_bounding_box(dataset):
    """Obtiene las coordenadas de una imagen satelital en formato EPSG:4326

    :param dataset: lector de conjunto de datos ráster
    :type dataset: rio.DatasetReader
    """
    # Obtiene el bounding box original
    origin_bb = dataset.bounds

    transformer = Transformer.from_crs(dataset.profile['crs'], 'epsg:4326')
    left, bottom = transformer.transform(origin_bb.left, origin_bb.bottom)
    right, top = transformer.transform(origin_bb.right, origin_bb.top)

    bounding_box = {
        'left': round(left, 3),
        'bottom': round(bottom, 3),
        'right': round(right, 3),
        'top': round(top, 3)
    }

    return bounding_box


def get_bounding_box_from_name(filename):
    """Obtiene las coordenadas de una imagen satelital en formato EPSG:4326

    :param filename: ruta de la imagen solicitada
    :type filename: str
    """
    file = open(filename, 'rb')
    data = file.read()

    try:
        with MemoryFile(data) as memfile:
            dataset = memfile.open()
    except rio.errors.RasterioIOError:
        print("Error. File not found!")

    return get_bounding_box(dataset)


def get_bounding_box_from_file(file):
    data = file.read()
    try:  # Intenta abrir la imagen. De no ser una imagen, se informa al cliente
        memfile = MemoryFile(data)
        dataset = memfile.open()
        return get_bounding_box(dataset)
    except rio.errors.RasterioIOError:
        response = {'error': 'File is not an image'}
        return response

def get_bounding_box_from_xml(file):
    data = minidom.parse(file)
    longs = [float(x.firstChild.data) for x in data.getElementsByTagName('LON')]
    lats = [float(x.firstChild.data) for x in data.getElementsByTagName('LAT')]
    top, bottom = max(lats), min(lats)
    left, right = min(longs), max(longs)

    bounding_box = {
        'left': round(bottom, 3),
        'bottom': round(left, 3),
        'right': round(top, 3),
        'top': round(right, 3)
    }

    return bounding_box

def rect_overlap(l1, r1, l2, r2):
    print(l1, r1, l2, r2)
    if l1[0] <= r2[0] or l2[0] <= r1[0]:
        return False

    if l1[1] >= r2[1] or l2[1] >= r1[1]:
        return False

    return True
