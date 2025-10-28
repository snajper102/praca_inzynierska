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
    alerts_view, comparison_view, live_widget_view,
    admin_dashboard, assign_house_view
)

router = DefaultRouter()
router.register(r'admin/houses', AdminHouseViewSet, basename='admin-houses')
router.register(r'admin/sensors', AdminSensorViewSet, basename='admin-sensors')
router.register(r'user/houses', UserHouseViewSet, basename='user-houses')
router.register(r'user/sensors', UserSensorViewSet, basename='user-sensors')
router.register(r'user/alerts', AlertViewSet, basename='user-alerts')

urlpatterns = [
    # API Routes
    path('', include(router.urls)),
    path('user/sensor/<int:sensor_id>/data/', sensor_data_view, name='sensor-data'),
    path('user/sensor/<int:sensor_id>/live/', live_data_view, name='live-data'),
    path('admin/sensor/data/', add_sensor_data, name='add-sensor-data'),
    path('admin/sensor/readings/', receive_sensor_readings, name='receive-sensor-readings'),

    # HTML Routes
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/sensor/<int:sensor_id>/', sensor_detail, name='sensor_detail'),
    path('alerts/', alerts_view, name='alerts'),
    path('comparison/<int:house_id>/', comparison_view, name='comparison'),
    path('widget/<int:sensor_id>/', live_widget_view, name='live_widget'),

    # Admin Routes
    path('admin-panel/', admin_dashboard, name='admin_dashboard'),
    path('admin-panel/assign/', assign_house_view, name='assign_house'),
]