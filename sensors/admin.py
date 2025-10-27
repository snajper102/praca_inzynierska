from django.contrib import admin
from .models import House, Sensor, SensorData

# Inline dla danych czujnika – pozwala dodawać odczyty bezpośrednio w widoku czujnika
class SensorDataInline(admin.TabularInline):
    model = SensorData
    extra = 1  # liczba pustych formularzy do dodania nowych danych
    fields = ('timestamp', 'voltage', 'current', 'power', 'energy', 'frequency', 'pf')
    readonly_fields = ('timestamp',)

# Inline dla czujników – umożliwia dodawanie czujników bezpośrednio przy dodawaniu domu
class SensorInline(admin.TabularInline):
    model = Sensor
    extra = 1  # liczba pustych formularzy dla nowych czujników
    fields = ('sensor_id', 'name', 'description')

@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'user')
    inlines = [SensorInline]
    search_fields = ('name', 'address', 'user__username')

@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('sensor_id', 'name', 'house', 'description')
    inlines = [SensorDataInline]
    search_fields = ('sensor_id', 'name', 'house__name')

@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ('sensor', 'timestamp', 'voltage', 'current', 'power', 'energy', 'frequency', 'pf')
    search_fields = ('sensor__sensor_id', 'timestamp')
