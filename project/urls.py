from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.authtoken import views as drf_views
from sensors.views import dashboard, register, profile, settings_view

# Customizacja admin panel
admin.site.site_header = "Energy Monitor - Panel Administracyjny"
admin.site.site_title = "Energy Monitor Admin"
admin.site.index_title = "Witaj w panelu administracyjnym"

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # API Authentication
    path('api-token-auth/', drf_views.obtain_auth_token, name='api-token-auth'),
    path('api/', include('sensors.urls')),

    # User Authentication
    path('', LoginView.as_view(template_name='login.html'), name='home'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
    path('register/', register, name='register'),

    # Dashboard & Profile & Settings
    path('dashboard/', dashboard, name='dashboard'),
    path('profile/', profile, name='profile'),
    path('settings/', settings_view, name='settings'),
]