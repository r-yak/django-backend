import os

import pandas
from django.db import transaction
from django.http import HttpRequest
from rest_framework import exceptions, status
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response

from api.core import predict
from api.models import Drug
from api.serializers import DrugSerializer


class SearchView(ListAPIView):
    serializer_class = DrugSerializer
    queryset = Drug.objects


class UploadView(CreateAPIView):
    serializer_class = DrugSerializer

    def create(self, request: HttpRequest, *args, **kwargs):
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


class PredictView(APIView):
    def post(self, request: HttpRequest, *args, **kwargs):
        file = request.FILES.get('image', None)
        if file is None:
            raise exceptions.ValidationError({'image': 'image 파일 필드가 주어지지 않았습니다.'})
        ext = os.path.splitext(file.name)[1]
        if ext not in ['.png', '.jpg']:
            raise exceptions.ValidationError({'image': f'지원되지 않는 파일 형식입니다. 받은 파일형식: {ext}'})
        return Response(predict(file), status=status.HTTP_200_OK)
