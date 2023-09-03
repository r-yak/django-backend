import pandas

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from api.core import converters
from api.core.algorithms import PredictionModel
from api.models import DrugFullSpecification
from api.serializers import DrugSerializer, PredictionSerializer


class SearchView(ListAPIView):
    serializer_class = DrugSerializer
    queryset = DrugFullSpecification.objects


class UploadView(CreateAPIView):
    serializer_class = DrugSerializer

    def create(self, request: Request, *args, **kwargs):
        for sheet in request.FILES.getlist('sheet'):
            df = pandas.read_excel(sheet)
            df = df.where(pandas.notnull(df), None)
            with transaction.atomic():
                for i in df.index:
                    data = dict(df.loc[i])
                    serializer = self.get_serializer(data=data)
                    serializer.is_valid(raise_exception=True)
                    self.perform_create(serializer)
        return Response({}, status=status.HTTP_201_CREATED)


class PredictView(CreateAPIView):
    serializer_class = PredictionSerializer
    image_field_name = 'raw_image'

    def perform_create(self, serializer: PredictionSerializer):
        requested_at = timezone.now()
        file: UploadedFile = serializer.validated_data[__class__.image_field_name]
        model = PredictionModel(converters.convert_file_to_mat(file))
        serializer.save(
            image=converters.convert_mat_to_file(model.mat, filename=file.name),
            mask_image=converters.convert_mat_to_file(model.bin_mat, filename=file.name),
            drug=model.drug,
            shape=model.shape,
            color=model.color,
            requested_at=requested_at,
        )
