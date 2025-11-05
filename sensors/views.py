import logging
from datetime import timedelta

from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg, Max, Min, Count # Zachowujemy ten import
from django.db import models # <-- POPRAWKA: Dodano brakujący import 'models'

try:
    from .forms import CustomUserCreationForm
except ImportError:
    from django.contrib.auth.forms import UserCreationForm as CustomUserCreationForm


from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
    action
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .models import House, Sensor, SensorData, Alert, UserSettings, ActivityLog
from .serializers import (
    HouseSerializer,
    SensorSerializer,
    SensorDataSerializer,
    SensorReadingSerializer,
    AlertSerializer,
    UserSettingsSerializer
)
from .utils import (
    calculate_reactive_power,
    check_alerts,
    log_activity,
    get_comparison_data,
    predict_monthly_cost,
    calculate_energy_for_period
)

logger = logging.getLogger(__name__)


# ========== REJESTRACJA I PROFILE ==========

def register(request):
    """Widok rejestracji nowego użytkownika"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password2') 

            UserSettings.objects.create(user=user)

            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

            log_activity(
                user=user,
                action='create',
                model_name='User',
                object_id=user.id,
                description=f"Utworzono nowe konto: {username}",
                request=request
            )

            messages.success(request, f'Konto utworzone pomyślnie! Witaj {username}!')
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if field != 'password2': 
                        messages.error(request, f"{error}")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'login.html', {'form': form})


@login_required
def profile(request):
    """Widok profilu użytkownika"""
    houses = House.objects.filter(user=request.user).prefetch_related('sensors')
    total_sensors = sum(house.sensors.count() for house in houses)
    settings, created = UserSettings.objects.get_or_create(user=request.user)
    total_alerts = Alert.objects.filter(house__user=request.user).count()
    unread_alerts = Alert.objects.filter(house__user=request.user, is_read=False).count()

    context = {
        'houses': houses,
        'total_sensors': total_sensors,
        'user_settings': settings,
        'total_alerts': total_alerts,
        'unread_alerts': unread_alerts,
    }
    return render(request, 'profile.html', context)


@login_required
def settings_view(request):
    """Widok ustawień użytkownika"""
    user_settings, created = UserSettings.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_settings.theme = request.POST.get('theme', 'dark')
        user_settings.email_alerts = request.POST.get('email_alerts') == 'on'
        user_settings.alert_frequency = request.POST.get('alert_frequency', 'immediate')
        user_settings.live_refresh_interval = int(request.POST.get('live_refresh_interval', 5))
        user_settings.show_predictions = request.POST.get('show_predictions') == 'on'

        monthly_goal = request.POST.get('monthly_goal_kwh')
        if monthly_goal:
            try:
                user_settings.monthly_goal_kwh = float(monthly_goal)
            except (ValueError, TypeError):
                user_settings.monthly_goal_kwh = None
        else:
            user_settings.monthly_goal_kwh = None

        user_settings.save()

        log_activity(
            user=request.user,
            action='update',
            model_name='UserSettings',
            object_id=user_settings.id,
            description="Zaktualizowano ustawienia użytkownika",
            request=request
        )

        messages.success(request, 'Ustawienia zapisane!')
        return redirect('settings')

    context = {
        'user_settings': user_settings,
    }
    return render(request, 'settings.html', context)


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

            reactive_power = calculate_reactive_power(
                reading['power'],
                reading['pf']
            )

            sensor_data = SensorData.objects.create(
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
            check_alerts(sensor, sensor_data)

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

    sensor_data = SensorData.objects.create(
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
    check_alerts(sensor, sensor_data)

    return Response(SensorDataSerializer(sensor_data).data, status=status.HTTP_201_CREATED)


# ========== VIEWSETS ==========

class AdminHouseViewSet(viewsets.ModelViewSet):
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        house = serializer.save()
        log_activity(
            user=self.request.user,
            action='create',
            model_name='House',
            object_id=house.id,
            description=f"Utworzono dom: {house.name} dla użytkownika {house.user.username}",
            request=self.request
        )

    def perform_update(self, serializer):
        house = serializer.save()
        log_activity(
            user=self.request.user,
            action='update',
            model_name='House',
            object_id=house.id,
            description=f"Zaktualizowano dom: {house.name}",
            request=self.request
        )

    def perform_destroy(self, instance):
        log_activity(
            user=self.request.user,
            action='delete',
            model_name='House',
            object_id=instance.id,
            description=f"Usunięto dom: {instance.name}",
            request=self.request
        )
        instance.delete()


class AdminSensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        sensor = serializer.save()
        log_activity(
            user=self.request.user,
            action='create',
            model_name='Sensor',
            object_id=sensor.id,
            description=f"Utworzono czujnik: {sensor.name} w domu {sensor.house.name}",
            request=self.request
        )

    def perform_update(self, serializer):
        sensor = serializer.save()
        log_activity(
            user=self.request.user,
            action='update',
            model_name='Sensor',
            object_id=sensor.id,
            description=f"Zaktualizowano czujnik: {sensor.name}",
            request=self.request
        )


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


class AlertViewSet(viewsets.ModelViewSet):
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Alert.objects.filter(house__user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        alert = self.get_object()
        alert.is_read = True
        alert.save()
        return Response({'status': 'marked as read'})

    @action(detail=True, methods=['post'])
    def mark_resolved(self, request, pk=None):
        alert = self.get_object()
        alert.is_resolved = True
        alert.save()
        return Response({'status': 'marked as resolved'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sensor_data_view(request, sensor_id):
    """API endpoint zwracający dane czujnika"""
    sensor = get_object_or_404(Sensor, id=sensor_id)
    if sensor.house.user != request.user:
        return Response({'error': 'Brak dostępu'}, status=status.HTTP_403_FORBIDDEN)
    
    start_date = timezone.now() - timedelta(days=1)
    qs = SensorData.objects.filter(
        sensor=sensor, 
        timestamp__gte=start_date
    ).order_by('timestamp')
    
    return Response(SensorDataSerializer(qs, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def live_data_view(request, sensor_id):
    """Endpoint do live widget - najnowsze dane"""
    sensor = get_object_or_404(Sensor, id=sensor_id)
    if sensor.house.user != request.user:
        return Response({'error': 'Brak dostępu'}, status=status.HTTP_403_FORBIDDEN)

    latest = sensor.data.order_by('-timestamp').first()
    if not latest:
        return Response({'error': 'Brak danych'}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'timestamp': latest.timestamp,
        'power': latest.power,
        'voltage': latest.voltage,
        'current': latest.current,
        'pf': latest.pf,
        'is_online': sensor.is_online,
    })


# ========== WIDOKI HTML ==========

@login_required
def dashboard(request):
    """Główny dashboard użytkownika z kosztami miesięcznymi"""
    houses = House.objects.filter(user=request.user).prefetch_related('sensors', 'sensors__data')
    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    all_sensors = Sensor.objects.filter(house__user=request.user)
    total_sensors = all_sensors.count()
    online_sensors = 0
    last_reading_time = None

    if total_sensors > 0:
        latest_data = SensorData.objects.filter(sensor__house__user=request.user).order_by('-timestamp').first()
        if latest_data:
            last_reading_time = latest_data.timestamp
        
        for sensor in all_sensors:
            if sensor.is_online:
                online_sensors += 1

    houses_with_costs = []
    for house in houses:
        sensors_in_house = house.sensors.all()
        total_energy_wh = 0
        total_power_now = 0
        sensor_count_in_house = 0

        for sensor in sensors_in_house:
            monthly_data = SensorData.objects.filter(
                sensor=sensor,
                timestamp__gte=start_of_month
            ).order_by('timestamp')

            if monthly_data.exists():
                data_list = list(monthly_data)
                for i in range(1, len(data_list)):
                    dt = (data_list[i].timestamp - data_list[i - 1].timestamp).total_seconds()
                    if dt > 0 and dt < 3600:
                        power = float(data_list[i].power) if data_list[i].power else 0
                        total_energy_wh += power * (dt / 3600.0)

                last_reading_in_sensor = data_list[-1]
                if last_reading_in_sensor and last_reading_in_sensor.power:
                    if (now - last_reading_in_sensor.timestamp) < timedelta(minutes=5):
                        total_power_now += float(last_reading_in_sensor.power)
                sensor_count_in_house += 1

        total_energy_kwh = total_energy_wh / 1000.0
        monthly_cost = total_energy_kwh * house.price_per_kwh
        prediction = predict_monthly_cost(house)
        comparison = get_comparison_data(house, 'month')

        houses_with_costs.append({
            'house': house,
            'monthly_kwh': round(total_energy_kwh, 2),
            'monthly_cost': round(monthly_cost, 2),
            'current_power': round(total_power_now, 0),
            'sensor_count': sensor_count_in_house,
            'prediction': prediction,
            'comparison': comparison,
        })

    unread_alerts = Alert.objects.filter(
        house__user=request.user,
        is_read=False
    ).order_by('-created_at')[:5]

    context = {
        'houses': houses,
        'houses_with_costs': houses_with_costs,
        'current_month': now.strftime('%B %Y'),
        'unread_alerts': unread_alerts,
        'total_sensors': total_sensors,
        'online_sensors': online_sensors,
        'last_reading_time': last_reading_time,
    }
    return render(request, 'dashboard.html', context)


@login_required
def sensor_detail(request, sensor_id):
    """
    Przebudowany widok szczegółów czujnika.
    Bez wykresów, skupiony na danych na żywo i podsumowaniach.
    """
    sensor = get_object_or_404(Sensor, id=sensor_id)
    if sensor.house.user != request.user:
        return HttpResponseForbidden("Brak dostępu")

    now = timezone.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    price_per_kwh = sensor.house.price_per_kwh

    # 1. Oblicz zużycie dzienne
    daily_kwh = calculate_energy_for_period(sensor.house, start_of_day, now, sensor_id=sensor.id)
    daily_cost = daily_kwh * price_per_kwh

    # 2. Oblicz zużycie miesięczne
    monthly_kwh = calculate_energy_for_period(sensor.house, start_of_month, now, sensor_id=sensor.id)
    monthly_cost = monthly_kwh * price_per_kwh

    # 3. Pobierz ostatnie 10 pomiarów do tabeli
    last_10_readings = SensorData.objects.filter(sensor=sensor).order_by('-timestamp')[:10]
    
    # 4. Pobierz średnią z ostatnich 5 pomiarów (zgodnie z prośbą)
    recent_readings = SensorData.objects.filter(sensor=sensor).order_by('-timestamp')[:5]
    avg_stats = recent_readings.aggregate(
        power=Avg('power'),
        voltage=Avg('voltage'),
        current=Avg('current'),
        pf=Avg('pf')
    )

    # 5. Pobierz ustawienia odświeżania (dla danych live)
    user_settings, _ = UserSettings.objects.get_or_create(user=request.user)

    context = {
        'sensor': sensor,
        'avg_stats': avg_stats, # Średnie dane
        'daily_kwh': daily_kwh,
        'daily_cost': daily_cost,
        'monthly_kwh': monthly_kwh,
        'monthly_cost': monthly_cost,
        'last_10_readings': last_10_readings,
        'refresh_interval': user_settings.live_refresh_interval,
    }
    return render(request, 'sensor_detail.html', context)


@login_required
def create_alert(request):
    """Widok formularza do ręcznego tworzenia alertów."""
    from .forms import AlertForm # Import AlertForm tutaj
    
    if request.method == 'POST':
        # Przekaż zalogowanego użytkownika do formularza
        form = AlertForm(request.POST, user=request.user)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.is_resolved = False 
            alert.save()
            
            log_activity(
                user=request.user,
                action='create',
                model_name='Alert',
                object_id=alert.id,
                description=f"Ręcznie utworzono alert: {alert.message}",
                request=request
            )
            
            messages.success(request, 'Pomyślnie utworzono nowy alert.')
            return redirect('alerts')
        else:
            messages.error(request, 'Formularz zawiera błędy. Popraw je.')
    else:
        # Przekaż użytkownika, aby formularz mógł filtrować domy
        form = AlertForm(user=request.user)

    context = {
        'form': form
    }
    return render(request, 'alert_create.html', context)


@login_required
def alerts_view(request):
    """Widok wszystkich alertów użytkownika"""
    alerts = Alert.objects.filter(house__user=request.user).order_by('-created_at')

    filter_type = request.GET.get('type')
    filter_severity = request.GET.get('severity')
    filter_status = request.GET.get('status')

    if filter_type:
        alerts = alerts.filter(alert_type=filter_type)
    if filter_severity:
        alerts = alerts.filter(severity=filter_severity)
    if filter_status == 'unread':
        alerts = alerts.filter(is_read=False)
    elif filter_status == 'resolved':
        alerts = alerts.filter(is_resolved=True)
    elif filter_status == 'active':
        alerts = alerts.filter(is_read=False, is_resolved=False)

    context = {
        'alerts': alerts[:50],
        'filter_type': filter_type,
        'filter_severity': filter_severity,
        'filter_status': filter_status,
    }
    return render(request, 'alerts.html', context)


@login_required
def comparison_view(request, house_id):
    """Widok porównań i statystyk"""
    house = get_object_or_404(House, id=house_id, user=request.user)

    day_comparison = get_comparison_data(house, 'day')
    week_comparison = get_comparison_data(house, 'week')
    month_comparison = get_comparison_data(house, 'month')
    prediction = predict_monthly_cost(house)

    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    sensor_rankings = []
    for sensor in house.sensors.all():
        total_kwh = calculate_energy_for_period(house, start_of_month, now, sensor_id=sensor.id)
        sensor_rankings.append({
            'sensor': sensor,
            'kwh': round(total_kwh, 2),
            'cost': round(total_kwh * house.price_per_kwh, 2)
        })

    sensor_rankings.sort(key=lambda x: x['kwh'], reverse=True)

    monthly_history = []
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    for i in range(12):
        if i == 0:
            month_start = current_month_start
            month_end = now
        else:
            month_end = current_month_start
            month_start = (month_end - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            current_month_start = month_start

        month_kwh = calculate_energy_for_period(house, month_start, month_end)
        monthly_history.append({
            'month': month_start.strftime('%b %Y'),
            'kwh': round(month_kwh, 2),
            'cost': round(month_kwh * house.price_per_kwh, 2)
        })

    monthly_history.reverse()

    context = {
        'house': house,
        'day_comparison': day_comparison,
        'week_comparison': week_comparison,
        'month_comparison': month_comparison,
        'prediction': prediction,
        'sensor_rankings': sensor_rankings,
        'monthly_history': monthly_history,
    }
    return render(request, 'comparison.html', context)


@login_required
def admin_dashboard(request):
    """Dashboard dla administratorów"""
    if not request.user.is_staff:
        return HttpResponseForbidden("Brak dostępu")
    
    total_users = User.objects.count()
    total_houses = House.objects.count()
    total_sensors = Sensor.objects.count()
    online_sensors = sum(1 for s in Sensor.objects.all() if s.is_online)

    unread_alerts = Alert.objects.filter(is_read=False).count()
    critical_alerts = Alert.objects.filter(severity='critical', is_resolved=False).count()

    recent_activity = ActivityLog.objects.all().order_by('-created_at')[:20]

    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    user_consumptions = []
    for user in User.objects.filter(is_active=True):
        houses = House.objects.filter(user=user)
        total_kwh = 0

        for house in houses:
            total_kwh += calculate_energy_for_period(house, start_of_month, now)

        if total_kwh > 0:
            user_consumptions.append({
                'user': user,
                'kwh': round(total_kwh, 2),
                'houses': houses.count()
            })

    user_consumptions.sort(key=lambda x: x['kwh'], reverse=True)

    context = {
        'total_users': total_users,
        'total_houses': total_houses,
        'total_sensors': total_sensors,
        'online_sensors': online_sensors,
        'offline_sensors': total_sensors - online_sensors,
        'unread_alerts': unread_alerts,
        'critical_alerts': critical_alerts,
        'recent_activity': recent_activity,
        'top_users': user_consumptions[:10],
    }
    return render(request, 'admin_dashboard.html', context)


@login_required
def admin_sensor_list_view(request):
    """Wyświetla pełną listę czujników z informacjami i linkami do edycji (dla admina)"""
    if not request.user.is_staff:
        return HttpResponseForbidden("Brak dostępu")
    
    # POPRAWKA: Przeniesienie importu models
    from django.db import models 

    # Używamy prefetch_related dla optymalizacji
    all_sensors = Sensor.objects.all().select_related('house').prefetch_related(
        models.Prefetch('data', queryset=SensorData.objects.order_by('-timestamp'), to_attr='last_reading_list')
    ).order_by('house__name', 'name')

    # Dodaj atrybut 'data.first()' dla wygody w szablonie (używając listy)
    for sensor in all_sensors:
        sensor.data.first = sensor.last_reading_list[0] if sensor.last_reading_list else None

    context = {
        'all_sensors': all_sensors
    }
    return render(request, 'admin_sensor_list.html', context)


@login_required
def assign_house_view(request):
    """Panel przypisywania domów do użytkowników (tylko admin)"""
    if not request.user.is_staff:
        return HttpResponseForbidden("Brak dostępu")

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        house_name = request.POST.get('house_name')
        address = request.POST.get('address', '')
        price_per_kwh = float(request.POST.get('price_per_kwh', 0.80))

        user = get_object_or_404(User, id=user_id)

        house = House.objects.create(
            user=user,
            name=house_name,
            address=address,
            price_per_kwh=price_per_kwh
        )

        log_activity(
            user=request.user,
            action='assign',
            model_name='House',
            object_id=house.id,
            description=f"Przypisano dom '{house_name}' do użytkownika {user.username}",
            request=request
        )

        messages.success(request, f"Dom '{house_name}' został przypisany do {user.username}")
        return redirect('assign_house')

    users = User.objects.filter(is_active=True).order_by('username')
    all_houses = House.objects.all().select_related('user').order_by('-created_at')[:50]

    context = {
        'users': users,
        'all_houses': all_houses,
    }
    return render(request, 'admin_assign.html', context)
