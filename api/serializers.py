from rest_framework import serializers

from api.models import DrugFullSpecification, Prediction


class DrugSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrugFullSpecification
        fields = '__all__'


class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = '__all__'
        read_only_fields = ['mask_image', 'color', 'drug', 'image', 'requested_at', 'shape']
