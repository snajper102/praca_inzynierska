from django.db import models

class House(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='houses')
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

class Sensor(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='sensors')
    sensor_id = models.CharField(max_length=100, unique=True, null=True, blank=True)  # identyfikator urządzenia, np. "pzem001"
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class SensorData(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='data')
    timestamp = models.DateTimeField()
    voltage = models.FloatField(null=True, blank=True)
    current = models.FloatField(null=True, blank=True)
    power = models.FloatField(null=True, blank=True)
    energy = models.FloatField(null=True, blank=True)
    frequency = models.FloatField(null=True, blank=True)
    pf = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.sensor.name} @ {self.timestamp}"
