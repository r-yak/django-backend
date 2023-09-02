import functools

import cv2


def preprocess(mat: cv2.Mat) -> cv2.Mat:
    mat = cv2.resize(mat, (256, 256))
    mat = _apply_whitebalance(mat) # 화이트 밸런싱 적용
    mat = _remove_background(mat) # 알약만 남기고 배경을 제거
    return mat


@functools.cache
def _get_white_balancer() -> cv2.xphoto.WhiteBalancer:
    return cv2.xphoto.createGrayworldWB()


@functools.cache
def _get_structuring_element() -> cv2.Mat:
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))


def _apply_whitebalance(bgr_image: cv2.Mat) -> cv2.Mat:
    lab_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2LAB)
    lab_image = _get_white_balancer().balanceWhite(lab_image)
    return cv2.cvtColor(lab_image, cv2.COLOR_LAB2BGR)


def _remove_background(bgr_image: cv2.Mat) -> cv2.Mat:
    raw_image = bgr_image.copy()
    bgr_image = cv2.bilateralFilter(bgr_image, -1, 32.0, 8.0)
    bin_image = cv2.Canny(bgr_image, 0, 255)
    bin_image = cv2.morphologyEx(bin_image, cv2.MORPH_CLOSE, _get_structuring_element())
    contours = cv2.findContours(bin_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]
    bin_image = cv2.drawContours(bin_image, contours, -1, 255, -1)
    return cv2.copyTo(raw_image, bin_image)
