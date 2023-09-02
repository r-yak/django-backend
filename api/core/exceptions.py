from rest_framework import status
from rest_framework.exceptions import APIException


class NotDetectedException(APIException):
    status_code = status.HTTP_204_NO_CONTENT
    default_detail = 'Detection failed.'
    default_code = 'detection_error'


class MultipleDetectedException(APIException):
    status_code = status.HTTP_406_NOT_ACCEPTABLE
    default_detail = 'Multiple items detected.'
    default_code = 'multiple_detection_error'


class ColorNotDetectedException(NotDetectedException):
    default_detail = 'Color detection failed.'
    default_code = 'color_detection_error'


class ShapeNotDetectedException(NotDetectedException):
    default_detail = 'Shape detection failed.'
    default_code = 'shape_detection_error'
