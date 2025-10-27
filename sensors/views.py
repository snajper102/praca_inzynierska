import logging
from datetime import timedelta

from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .models import House, Sensor, SensorData
from .serializers import (
    HouseSerializer,
    SensorSerializer,
    SensorDataSerializer,
    SensorReadingSerializer
)

logger = logging.getLogger(__name__)


# ========== REJESTRACJA I PROFILE ==========

def register(request):
    """Widok rejestracji nowego użytkownika"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, f'Konto utworzone pomyślnie! Witaj {username}!')
            return redirect('dashboard')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = UserCreationForm()
    return render(request, 'login.html', {'form': form})


@login_required
def profile(request):
    """Widok profilu użytkownika"""
    houses = House.objects.filter(user=request.user).prefetch_related('sensors')
    total_sensors = sum(house.sensors.count() for house in houses)

    context = {
        'houses': houses,
        'total_sensors': total_sensors,
    }
    return render(request, 'profile.html', context)


# ========== FUNKCJE POMOCNICZE ==========

def calculate_reactive_power(power, pf):
    """
    Oblicza moc bierną Q [VAR] na podstawie mocy czynnej P i współczynnika mocy PF

    Q = sqrt(S² - P²)
    gdzie S = P / PF (moc pozorna)
    """
    if pf == 0 or power == 0:
        return 0
    try:
        S = power / pf  # Moc pozorna [VA]
        Q = (S ** 2 - power ** 2) ** 0.5  # Moc bierna [VAR]
        return round(Q, 2)
    except:
        return 0


# ========== API ENDPOINTS ==========

@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def receive_sensor_readings(request):
    """Endpoint do odbierania danych z czujników"""
    serializer = SensorReadingSerializer(data=request.data, many=True)
    if serializer.is_valid():
        for reading in serializer.validated_data:
            try:
                sensor = Sensor.objects.get(sensor_id=reading['sensor_id'])
            except Sensor.DoesNotExist:
                logger.warning(f"Sensor {reading['sensor_id']} nie istnieje.")
                continue

            # Oblicz moc bierną (Reactive Power)
            reactive_power = calculate_reactive_power(
                reading['power'],
                reading['pf']
            )

            SensorData.objects.create(
                sensor=sensor,
                timestamp=reading['timestamp'],
                voltage=reading['voltage'],
                current=reading['current'],
                power=reading['power'],
                energy=reading['energy'],
                frequency=reading['frequency'],
                pf=reading['pf'],
                reactive_power=reactive_power
            )
        return Response({"status": "ok"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def add_sensor_data(request, sensor_id):
    """Dodaj pojedynczy pomiar do czujnika"""
    sensor = get_object_or_404(Sensor, id=sensor_id)
    required = ['voltage', 'current', 'power', 'energy', 'frequency', 'pf']
    missing = [f for f in required if f not in request.data]
    if missing:
        return Response(
            {'error': f"Brak danych: {', '.join(missing)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    reactive_power = calculate_reactive_power(
        float(request.data['power']),
        float(request.data['pf'])
    )

    sd = SensorData.objects.create(
        sensor=sensor,
        timestamp=timezone.now(),
        voltage=request.data['voltage'],
        current=request.data['current'],
        power=request.data['power'],
        energy=request.data['energy'],
        frequency=request.data['frequency'],
        pf=request.data['pf'],
        reactive_power=reactive_power
    )
    return Response(SensorDataSerializer(sd).data, status=status.HTTP_201_CREATED)


# ========== VIEWSETS DLA ADMIN/USER ==========

class AdminHouseViewSet(viewsets.ModelViewSet):
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    permission_classes = [IsAdminUser]


class AdminSensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    permission_classes = [IsAdminUser]


class UserHouseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = HouseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return House.objects.filter(user=self.request.user)


class UserSensorViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SensorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        houses = House.objects.filter(user=self.request.user)
        return Sensor.objects.filter(house__in=houses)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sensor_data_view(request, sensor_id):
    """API endpoint zwracający dane czujnika"""
    sensor = get_object_or_404(Sensor, id=sensor_id)
    if sensor.house.user != request.user:
        return Response({'error': 'Brak dostępu'}, status=status.HTTP_403_FORBIDDEN)
    qs = SensorData.objects.filter(sensor=sensor).order_by('timestamp')
    return Response(SensorDataSerializer(qs, many=True).data)


# ========== WIDOKI HTML ==========

@login_required
def dashboard(request):
    """Główny dashboard użytkownika"""
    houses = House.objects.filter(user=request.user).prefetch_related('sensors__data')
    return render(request, 'dashboard.html', {'houses': houses})


@login_required
def sensor_detail(request, sensor_id):
    """Szczegółowy widok czujnika z wykresami"""
    sensor = get_object_or_404(Sensor, id=sensor_id)
    if sensor.house.user != request.user:
        return HttpResponseForbidden("Brak dostępu")

    data_qs = SensorData.objects.filter(sensor=sensor).order_by('timestamp')

    # Przygotowanie danych do wykresów
    timestamps = [d.timestamp.strftime("%H:%M:%S") for d in data_qs]
    voltages = [float(d.voltage) if d.voltage else 0 for d in data_qs]
    currents = [float(d.current) if d.current else 0 for d in data_qs]
    powers = [float(d.power) if d.power else 0 for d in data_qs]

    # Oblicz energię przez całkowanie mocy
    energy_wh = []
    for i in range(1, len(data_qs)):
        dt = (data_qs[i].timestamp - data_qs[i - 1].timestamp).total_seconds()
        energy_wh.append(powers[i] * dt / 3600.0)

    energy_times = [d.timestamp for d in data_qs[1:]]

    now = timezone.now()
    last_hour = now - timedelta(hours=1)
    start_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Agregacja energii
    total_wh_last_hour = sum(e for t, e in zip(energy_times, energy_wh) if t >= last_hour)
    total_wh_today = sum(e for t, e in zip(energy_times, energy_wh) if t >= start_day)

    hourly_kwh = total_wh_last_hour / 1000.0
    daily_kwh = total_wh_today / 1000.0

    # Oblicz koszt energii
    PRICE_PER_KWH = sensor.house.price_per_kwh
    daily_cost = daily_kwh * PRICE_PER_KWH
    hourly_cost = hourly_kwh * PRICE_PER_KWH

    context = {
        'sensor': sensor,
        'data_qs': data_qs,
        'timestamps': timestamps,
        'voltages': voltages,
        'currents': currents,
        'powers': powers,
        'hourly_kwh': hourly_kwh,
        'daily_kwh': daily_kwh,
        'daily_cost': daily_cost,
        'hourly_cost': hourly_cost,
    }
    return render(request, 'sensor_detail.html', context)