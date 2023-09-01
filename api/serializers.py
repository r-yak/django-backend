from rest_framework import serializers

from api.models import Drug


class DrugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drug
        fields = '__all__'


class DrugPredictionSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='ITEM_NAME')
    dosage_form = serializers.SerializerMethodField()
    dosage = serializers.SerializerMethodField()
    dosage_unit = serializers.SerializerMethodField()
    shape = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()

    class Meta:
        model = Drug
        fields = [
            'name',
            'dosage_form',
            'dosage',
            'dosage_unit',
            'shape',
            'color',
        ]

    def get_dosage_form(self, obj: Drug):
        return ''

    def get_dosage(self, obj: Drug):
        return ''

    def get_dosage_unit(self, obj: Drug):
        return ''

    def get_shape(self, obj: Drug):
        return ''

    def get_color(self, obj: Drug):
        return ''
