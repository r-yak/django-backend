import pandas
from django.db import transaction
from django.http import HttpRequest
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response

from api.models import Drug
from api.serializers import DrugSerializer


class PredictView(ListAPIView):
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
