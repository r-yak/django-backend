import functools
import typing

import cv2
import cv2.typing
import numpy

from api.core import exceptions
from api.models import ColorChoices, Drug, ShapeChoices


class PredictionModel:
    IMG_SHAPE = (256, 256)
    APPROX_EPSILON = 0.04
    CIRCLE_VERTICES = 7

    raw_mat: cv2.typing.MatLike
    mat: cv2.typing.MatLike
    contour: typing.Sequence[cv2.typing.MatLike]

    def __init__(self, mat: cv2.typing.MatLike) -> None:
        self.raw_mat = self._resize(mat)
        self.mat = self._white_balance(self.raw_mat)
        self.contour = self._find_contour(self.mat)
        self.mat = self._remove_background(self.raw_mat, self.contour)

    def _resize(self, mat: cv2.typing.MatLike) -> cv2.typing.MatLike:
        return cv2.resize(mat, __class__.IMG_SHAPE)

    def _white_balance(self, mat: cv2.typing.MatLike) -> cv2.typing.MatLike:
        mat = cv2.cvtColor(mat, cv2.COLOR_BGR2LAB)
        mat = _get_white_balancer().balanceWhite(mat)
        return cv2.cvtColor(mat, cv2.COLOR_LAB2BGR)

    def _find_contour(self, mat: cv2.typing.MatLike) -> typing.Sequence[cv2.typing.MatLike]:
        mat = cv2.bilateralFilter(mat, -1, 32.0, 8.0)
        bin_mat = cv2.Canny(mat, 0, 255)
        bin_mat = cv2.morphologyEx(bin_mat, cv2.MORPH_CLOSE, _get_structuring_element())
        contours = cv2.findContours(bin_mat, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]
        if not contours:
            # TODO: 검출 실패한 데이터 수집
            raise exceptions.NotDetectedException('알약이 검출되지 않았습니다.')
        return max(contours, key=lambda cont:cv2.arcLength(cont, True))

    def _remove_background(self, mat: cv2.typing.MatLike, contour: typing.Sequence[cv2.typing.MatLike]) -> cv2.typing.MatLike:
        bin_mat = numpy.zeros(mat.shape[:2], dtype=numpy.uint8)
        mask = cv2.drawContours(bin_mat, [contour], -1, 255, -1)
        return cv2.copyTo(mat, mask)

    def predict_shape(self) -> ShapeChoices:
        arc_length = cv2.arcLength(self.contour, True)
        approx_contour = cv2.approxPolyDP(self.contour, __class__.APPROX_EPSILON * arc_length, True)
        n_vertices = len(approx_contour)
        if n_vertices == 3:
            return ShapeChoices.TRIANGLE
        elif n_vertices == 4:
            return ShapeChoices.RECTANGLE
        elif n_vertices == 5:
            return ShapeChoices.PENTAGON
        elif n_vertices < __class__.CIRCLE_VERTICES:
            return ShapeChoices.OVAL
        else:
            return ShapeChoices.CIRCLE

    def predict_color(self) -> ColorChoices:
        return ColorChoices.UNKNOWN

    def predict_drug(self) -> typing.Optional[Drug]:
        return None


@functools.cache
def _get_white_balancer() -> cv2.xphoto.WhiteBalancer:
    return cv2.xphoto.createGrayworldWB()


@functools.cache
def _get_structuring_element() -> cv2.Mat:
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
