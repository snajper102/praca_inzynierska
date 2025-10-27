from django.db import models
from django.contrib.auth.models import User


class House(models.Model):
    """Model domu/lokalizacji"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='houses')
    name = models.CharField(max_length=100, verbose_name="Nazwa")
    address = models.CharField(max_length=255, blank=True, verbose_name="Adres")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")
    price_per_kwh = models.FloatField(default=0.80, verbose_name="Cena za kWh [PLN]")

    class Meta:
        verbose_name = "Dom"
        verbose_name_plural = "Domy"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class Sensor(models.Model):
    """Model czujnika PZEM-004T"""
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='sensors')
    sensor_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        verbose_name="ID czujnika"
    )
    name = models.CharField(max_length=100, verbose_name="Nazwa")
    description = models.TextField(blank=True, verbose_name="Opis")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data dodania")
    is_active = models.BooleanField(default=True, verbose_name="Aktywny")

    class Meta:
        verbose_name = "Czujnik"
        verbose_name_plural = "Czujniki"
        ordering = ['house', 'name']

    def __str__(self):
        return f"{self.name} - {self.house.name}"


class SensorData(models.Model):
    """Dane z czujnika PZEM-004T v3"""
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='data')
    timestamp = models.DateTimeField(verbose_name="Czas pomiaru", db_index=True)

    # Podstawowe pomiary z PZEM-004T
    voltage = models.FloatField(null=True, blank=True, verbose_name="Napięcie [V]")
    current = models.FloatField(null=True, blank=True, verbose_name="Prąd [A]")
    power = models.FloatField(null=True, blank=True, verbose_name="Moc czynna [W]")
    energy = models.FloatField(null=True, blank=True, verbose_name="Energia [kWh]")
    frequency = models.FloatField(null=True, blank=True, verbose_name="Częstotliwość [Hz]")
    pf = models.FloatField(null=True, blank=True, verbose_name="Współczynnik mocy")

    # Obliczona moc bierna
    reactive_power = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Moc bierna [VAR]",
        help_text="Obliczona na podstawie mocy czynnej i współczynnika mocy"
    )

    class Meta:
        verbose_name = "Pomiar"
        verbose_name_plural = "Pomiary"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['sensor', '-timestamp']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.sensor.name} @ {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    @property
    def apparent_power(self):
        """Oblicza moc pozorną S [VA]"""
        if self.pf and self.pf != 0 and self.power:
            return self.power / self.pf
        return 0