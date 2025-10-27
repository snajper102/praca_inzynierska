from rest_framework import serializers
from .models import House, Sensor, SensorData


class SensorReadingSerializer(serializers.Serializer):
    sensor_id = serializers.CharField()
    timestamp = serializers.DateTimeField()
    voltage = serializers.FloatField()
    current = serializers.FloatField()
    power = serializers.FloatField()
    energy = serializers.FloatField()
    frequency = serializers.FloatField()
    pf = serializers.FloatField()

class HouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = House
        fields = ['id', 'user', 'name', 'address']


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ['id', 'house', 'name', 'description']


from django.utils import timezone
from .models import SensorData


class SensorDataSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%S",
        default_timezone=timezone.utc,
        read_only=True
    )

    class Meta:
        model = SensorData
        fields = ['id', 'sensor', 'timestamp', 'voltage', 'current', 'power', 'energy', 'frequency', 'pf']
        read_only_fields = ['timestamp']
