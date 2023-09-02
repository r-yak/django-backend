import dataclasses
import functools
import re
import typing

import colorgram
import colour
import cv2
import cv2.typing
import numpy
import PIL.Image

from api.core import exceptions
from api.models import ColorChoices, Drug, ShapeChoices


@dataclasses.dataclass
class _MunsellColor:
    hue: float
    value: float
    chroma: float
    code: float

    COLOR_CHOICES_MUNSELL_HUE_CODES = {
        2: ColorChoices.BLUE_GREEN, # "BG"
        4: ColorChoices.YELLOW_GREEN, # "GY"
        6: ColorChoices.ORANGE, # "YR"
        8: ColorChoices.REDDISH_PURPLE, # "RP"
        10: ColorChoices.BLUISH_VIOLET, # "PB"
        1: ColorChoices.BLUE, # "B"
        3: ColorChoices.GREEN, # "G"
        5: ColorChoices.YELLOW, # "Y"
        7: ColorChoices.RED, # "R"
        9: ColorChoices.BLUISH_PURPLE, # "P"
    }

    def to_color_choice(self) -> ColorChoices:
        if self._is_colorless():
            return self._to_color_choices_colorless()
        return __class__.COLOR_CHOICES_MUNSELL_HUE_CODES[round(self.code, 1)]

    def _is_colorless(self) -> bool:
        return self.chroma < 4.0 or self.value < 2.0 or self.value > 9.0 or round(self.code, 1) == 0

    def _to_color_choices_colorless(self) -> ColorChoices:
        if self.value < 2.5:
            return ColorChoices.BLACK
        elif self.value < 7.0:
            return ColorChoices.GRAY
        else:
            return ColorChoices.WHITE


class PredictionModel:
    IMG_SHAPE = (256, 256)
    APPROX_EPSILON = 0.04
    CIRCLE_VERTICES = 7

    raw_mat: cv2.typing.MatLike
    mat: cv2.typing.MatLike
    contour: typing.Sequence[cv2.typing.MatLike]
    shape: ShapeChoices
    color: ColorChoices
    drug: typing.Optional[Drug]

    def __init__(self, mat: cv2.typing.MatLike) -> None:
        self.raw_mat = self._resize(mat)
        self.mat = self._white_balance(self.raw_mat)
        self.contour = self._find_contour(self.mat)
        self.mat = self._remove_background(self.raw_mat, self.contour)
        self.shape = self._predict_shape()
        self.color = self._predict_color()
        self.drug = self._predict_drug()

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

    def _predict_shape(self) -> ShapeChoices:
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

    def _predict_color(self) -> ColorChoices:
        colors: typing.List[colorgram.Color]
        mat = cv2.resize(self.mat, (64, 64))
        mat = cv2.bilateralFilter(mat, -1, 32.0, 8.0)
        mat = cv2.cvtColor(mat, cv2.COLOR_BGR2RGB)
        img = PIL.Image.fromarray(mat)
        colors = colorgram.extract(img, 2)
        if len(colors) < 2:
            raise exceptions.ColorNotDetectedException('색상이 검출되지 않았습니다.')
        color = colors[1] # colors[0]는 가장 많은 색상 = 배경 색상이므로 무시한다.
        munsell = self._to_munsell(color)
        print(munsell)
        return munsell.to_color_choice()

    def _to_munsell(self, color: colorgram.Color) -> _MunsellColor:
        """colorgram이 감지한 색상을 Munsell 색 체계로 변환"""
        color_rgb = list(map(lambda x: x / 255.0, color.rgb))
        color_XYZ = colour.RGB_to_XYZ(color_rgb, colour.models.RGB_COLOURSPACE_sRGB)
        color_xyY = colour.XYZ_to_xyY(color_XYZ)
        color_munsell = colour.notation.munsell.xyY_to_munsell_specification(color_xyY)
        return _MunsellColor(
            hue=color_munsell[0],
            value=color_munsell[1],
            chroma=color_munsell[2],
            code=color_munsell[3],
        )

    def _predict_drug(self) -> typing.Optional[Drug]:
        return Drug.objects.filter(
            color=self.color,
            shape=self.shape,
        ).first()


@functools.cache
def _get_white_balancer() -> cv2.xphoto.WhiteBalancer:
    return cv2.xphoto.createGrayworldWB()


@functools.cache
def _get_structuring_element() -> cv2.Mat:
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
