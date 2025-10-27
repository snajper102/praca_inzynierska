from rest_framework import serializers
from django.utils import timezone
from .models import House, Sensor, SensorData


class SensorReadingSerializer(serializers.Serializer):
    """Serializer dla odczytów z czujnika"""
    sensor_id = serializers.CharField()
    timestamp = serializers.DateTimeField()
    voltage = serializers.FloatField()
    current = serializers.FloatField()
    power = serializers.FloatField()
    energy = serializers.FloatField()
    frequency = serializers.FloatField()
    pf = serializers.FloatField()


class HouseSerializer(serializers.ModelSerializer):
    """Serializer dla modelu House"""
    class Meta:
        model = House
        fields = ['id', 'user', 'name', 'address', 'price_per_kwh', 'created_at']
        read_only_fields = ['created_at']


class SensorSerializer(serializers.ModelSerializer):
    """Serializer dla modelu Sensor"""
    class Meta:
        model = Sensor
        fields = ['id', 'house', 'sensor_id', 'name', 'description', 'is_active', 'created_at']
        read_only_fields = ['created_at']


class SensorDataSerializer(serializers.ModelSerializer):
    """Serializer dla modelu SensorData"""
    timestamp = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%S",
        default_timezone=timezone.utc,
        read_only=True
    )

    class Meta:
        model = SensorData
        fields = [
            'id',
            'sensor',
            'timestamp',
            'voltage',
            'current',
            'power',
            'energy',
            'frequency',
            'pf',
            'reactive_power'
        ]
        read_only_fields = ['timestamp', 'reactive_power']