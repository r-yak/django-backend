import cv2
import numpy

from django.core.files import File
from django.core.files.base import ContentFile


def convert_file_to_mat(file: File) -> cv2.Mat:
    buf = numpy.asarray(bytearray(file.file.read()), dtype=numpy.uint8)
    return cv2.imdecode(buf, cv2.IMREAD_COLOR)


def convert_mat_to_file(mat: cv2.Mat) -> File:
    ret, buf = cv2.imencode('.png', mat)
    return ContentFile(buf.tobytes(), name='preprocessed.png')
