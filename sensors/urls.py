from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # API ViewSets
    AdminHouseViewSet, AdminSensorViewSet,
    UserHouseViewSet, UserSensorViewSet, AlertViewSet,
    # API Functions
    sensor_data_view, add_sensor_data, receive_sensor_readings, live_data_view,
    # HTML Views
    dashboard, sensor_detail, register, profile, settings_view,
    alerts_view, create_alert, comparison_view, 
    admin_dashboard, assign_house_view,
    admin_sensor_list_view, # <-- NOWY WIDOK
)

# --- ŚCIEŻKI API ---
router = DefaultRouter()
router.register(r'admin/houses', AdminHouseViewSet, basename='admin-houses')
router.register(r'admin/sensors', AdminSensorViewSet, basename='admin-sensors')
router.register(r'user/houses', UserHouseViewSet, basename='user-houses')
router.register(r'user/sensors', UserSensorViewSet, basename='user-sensors')
router.register(r'user/alerts', AlertViewSet, basename='user-alerts')

api_urlpatterns = [
    path('', include(router.urls)),
    path('user/sensor/<int:sensor_id>/data/', sensor_data_view, name='sensor-data'),
    path('user/sensor/<int:sensor_id>/live/', live_data_view, name='live-data'),
    path('admin/sensor/data/', add_sensor_data, name='add-sensor-data'),
    path('admin/sensor/readings/', receive_sensor_readings, name='receive-sensor-readings'),
]

# --- ŚCIEŻKI HTML (WEB) ---
html_urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/sensor/<int:sensor_id>/', sensor_detail, name='sensor_detail'),
    path('profile/', profile, name='profile'),
    path('settings/', settings_view, name='settings'),
    
    path('alerts/create/', create_alert, name='alert_create'), 
    path('alerts/', alerts_view, name='alerts'),
    path('comparison/<int:house_id>/', comparison_view, name='comparison'),
    
    # NOWE ŚCIEŻKI ADMINA
    path('admin-panel/', admin_dashboard, name='admin_dashboard'),
    path('admin-panel/sensors/', admin_sensor_list_view, name='admin_sensor_list'), # <-- NOWA LISTA
    path('admin-panel/assign/', assign_house_view, name='assign_house'),
]

urlpatterns = api_urlpatterns + html_urlpatterns
