from django.contrib import admin
from .models import House, Sensor, SensorData


class SensorDataInline(admin.TabularInline):
    """Inline dla danych czujnika"""
    model = SensorData
    extra = 0
    fields = ('timestamp', 'voltage', 'current', 'power', 'energy', 'frequency', 'pf', 'reactive_power')
    readonly_fields = ('timestamp', 'reactive_power')
    can_delete = False
    max_num = 10  # Pokaż tylko 10 ostatnich

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('-timestamp')[:10]


class SensorInline(admin.TabularInline):
    """Inline dla czujników"""
    model = Sensor
    extra = 1
    fields = ('sensor_id', 'name', 'description', 'is_active')


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'address', 'price_per_kwh', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('name', 'address', 'user__username')
    inlines = [SensorInline]
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Informacje podstawowe', {
            'fields': ('user', 'name', 'address')
        }),
        ('Ustawienia', {
            'fields': ('price_per_kwh',)
        }),
        ('Informacje systemowe', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('name', 'sensor_id', 'house', 'is_active', 'created_at')
    list_filter = ('is_active', 'house', 'created_at')
    search_fields = ('sensor_id', 'name', 'house__name', 'description')
    inlines = [SensorDataInline]
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Informacje podstawowe', {
            'fields': ('house', 'sensor_id', 'name', 'description')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Informacje systemowe', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = (
        'sensor',
        'timestamp',
        'voltage',
        'current',
        'power',
        'reactive_power',
        'energy',
        'frequency',
        'pf'
    )
    list_filter = ('sensor', 'timestamp')
    search_fields = ('sensor__sensor_id', 'sensor__name')
    readonly_fields = ('timestamp', 'reactive_power')
    date_hierarchy = 'timestamp'

    fieldsets = (
        ('Czujnik', {
            'fields': ('sensor', 'timestamp')
        }),
        ('Parametry elektryczne', {
            'fields': (
                ('voltage', 'current'),
                ('power', 'reactive_power'),
                ('frequency', 'pf'),
                'energy'
            )
        }),
    )

    def has_add_permission(self, request):
        """Wyłącz ręczne dodawanie danych przez admin"""
        return False