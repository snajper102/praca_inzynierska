from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdminHouseViewSet, AdminSensorViewSet,
    UserHouseViewSet, UserSensorViewSet,
    sensor_data_view, add_sensor_data, receive_sensor_readings,
    dashboard, sensor_detail
)

router = DefaultRouter()
router.register(r'admin/houses', AdminHouseViewSet, basename='admin-houses')
router.register(r'admin/sensors', AdminSensorViewSet, basename='admin-sensors')
router.register(r'user/houses', UserHouseViewSet, basename='user-houses')
router.register(r'user/sensors', UserSensorViewSet, basename='user-sensors')

urlpatterns = [
    path('', include(router.urls)),
    path('user/sensor/<int:sensor_id>/data/', sensor_data_view, name='sensor-data'),
    path('admin/sensor/data/', add_sensor_data, name='add-sensor-data'),
    path('admin/sensor/readings/', receive_sensor_readings, name='receive-sensor-readings'),
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/sensor/<int:sensor_id>/', sensor_detail, name='sensor_detail'),
]