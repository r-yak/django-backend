from django.core.validators import FileExtensionValidator
from django.db import models


class DrugFullSpecification(models.Model):
    ITEM_SEQ = models.IntegerField(verbose_name="품목일련번호")
    ITEM_NAME = models.CharField(verbose_name="품목명", max_length=4000)
    ENTP_SEQ = models.IntegerField(verbose_name="업체일련번호")
    ENTP_NAME = models.CharField(verbose_name="업체명", max_length=300)
    CHARTN = models.CharField(verbose_name="성상", max_length=4000)
    ITEM_IMAGE = models.CharField(verbose_name="큰제품이미지", max_length=100, null=True)
    PRINT_FRONT = models.CharField(verbose_name="표시(앞)", max_length=200, null=True)
    PRINT_BACK = models.CharField(verbose_name="표시(뒤)", max_length=200, null=True)
    DRUG_SHAPE = models.CharField(verbose_name="의약품모양", max_length=20)
    COLOR_CLASS1 = models.CharField(verbose_name="색깔(앞)", max_length=200)
    COLOR_CLASS2 = models.CharField(verbose_name="색깔(뒤)", max_length=200, null=True)
    LINE_FRONT = models.CharField(verbose_name="분할선(앞)", max_length=40, null=True)
    LINE_BACK = models.CharField(verbose_name="분할선(뒤)", max_length=40, null=True)
    LENG_LONG = models.CharField(verbose_name="크기(장축)", max_length=20, null=True)
    LENG_SHORT = models.CharField(verbose_name="크기(단축)", max_length=20, null=True)
    THICK = models.CharField(verbose_name="크기(두께)", max_length=30, null=True)
    IMG_REGIST_TS = models.DateField (verbose_name="약학정보원이미지생성일")
    CLASS_NO = models.IntegerField(verbose_name="분류번호")
    ETC_OTC_CODE = models.IntegerField(verbose_name="전문/일반")
    ITEM_PERMIT_DATE = models.DateField (verbose_name="품목허가일자")
    SHAPE_CODE = models.IntegerField(verbose_name="제형코드")
    MARK_CODE_FRONT_ANAL = models.CharField(verbose_name="마크내용(앞)", max_length=30, null=True)
    MARK_CODE_BACK_ANAL = models.CharField(verbose_name="마크내용(뒤)", max_length=30, null=True)
    MARK_CODE_FRONT_IMG = models.CharField(verbose_name="마크이미지(앞)", max_length=100, null=True)
    MARK_CODE_BACK_IMG = models.CharField(verbose_name="마크이미지(뒤)", max_length=100, null=True)
    ITEM_ENG_NAME = models.CharField(verbose_name="제품영문명", max_length=2000, null=True, blank=True)
    EDI_CODE = models.CharField(verbose_name="보험코드", max_length=100, null=True)


class ColorChoices(models.TextChoices):
    RED = 'red', 'R - 빨강(적)'
    ORANGE = 'orange', 'O - 주황'
    YELLOW = 'yellow', 'Y - 노랑(황)'
    YELLOW_GREEN = 'yellow-green', 'YG - 연두'
    GREEN = 'green', 'G - 초록(녹)'
    BLUE_GREEN = 'blue-green', 'BG - 청록'
    BLUE = 'blue', 'B - 파랑(청)'
    BLUISH_VIOLET = 'bluish-violet', 'bV - 남색(남)'
    BLUISH_PURPLE = 'bluish-purple', 'bP - 보라'
    REDDISH_PURPLE = 'reddish-purple', 'rP - 자주(자)'
    PINK = 'pink', 'Pk - 분홍'
    BROWN = 'brown', 'Br - 갈색(갈)'
    WHITE = 'white', 'W - 하양(백)'
    GRAY = 'gray', 'Gy - 회색(회)'
    BLACK = 'black', 'Bk - 검정(흑)'
    UNKNOWN = 'unknown', '검출 실패'


class ShapeChoices(models.TextChoices):
    CIRCLE = 'circle', '원형'
    OVAL = 'oval', '타원형'
    SEMICIRCLE = 'semicircle', '반원형'
    OBLONG = 'oblong', '장방형'
    SQUARE = 'square', '정사각형'
    RECTANGLE = 'rectangle', '직사각형'
    DIAMOND = 'diamond', '다이아몬드형'
    TRIANGLE = 'triangle', '삼각형'
    PENTAGON = 'pentagon', '오각형'
    HEXAGON = 'hexagon', '육각형'
    OCTAGON = 'octagon', '팔각형'
    UNKNOWN = 'unknown', '검출 실패'


class DosageFormChoices(models.TextChoices):
    CAPSULE = 'capsule', '캡슐'
    TABLET = 'tablet', '정제'


class DosageUnitChoices(models.TextChoices):
    MILI_GRAM = 'mg', '밀리그램'
    MICRO_GRAM = 'mcg', '마이크로그램'
    GRAM = 'g', '그램'
    MILI_LITER = 'mL', '밀리리터'
    PERCENT = '%', '퍼센트'


class Drug(models.Model):
    specification = models.ForeignKey(DrugFullSpecification, on_delete=models.DO_NOTHING, null=True)
    name = models.CharField(max_length=4000)
    dosage_form = models.TextField(choices=DosageFormChoices.choices)
    dosage = models.IntegerField(null=True)
    dosage_unit = models.TextField(choices=DosageUnitChoices.choices, null=True)
    shape = models.TextField(choices=ShapeChoices.choices)
    color = models.TextField(choices=ColorChoices.choices)


class Prediction(models.Model):
    raw_image = models.ImageField(upload_to='prediction/image-raw/', validators=[FileExtensionValidator(['jpg', 'png'])])
    image = models.ImageField(upload_to='prediction/image/')
    drug = models.ForeignKey(Drug, on_delete=models.SET_NULL, null=True)
    shape = models.TextField(choices=ShapeChoices.choices)
    color = models.TextField(choices=ColorChoices.choices)
    created_at = models.DateTimeField(auto_now=True)
    requested_at = models.DateTimeField()
