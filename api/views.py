from rest_framework.generics import ListAPIView

from api.models import Drug
from api.serializers import DrugSerializer


class PredictView(ListAPIView):
    serializer_class = DrugSerializer
    queryset = Drug.objects
