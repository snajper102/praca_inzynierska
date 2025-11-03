
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.authtoken import views as drf_views
from sensors.views import register  # Potrzebujemy tylko tego jednego widoku tutaj

# Customizacja admin panel
admin.site.site_header = "Energy Monitor - Panel Administracyjny"
admin.site.site_title = "Energy Monitor Admin"
admin.site.index_title = "Witaj w panelu administracyjnym"

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # API Authentication (To jest poprawne)
    path('api-token-auth/', drf_views.obtain_auth_token, name='api-token-auth'),

    # POPRAWKA: Dołączaj ścieżki API z 'sensors.urls' pod prefiksem /api/
    # (Zakładając, że sensors.urls zawiera router DRF na ścieżce '')
    path('api/', include('sensors.urls')),

    # User Authentication
    path('', LoginView.as_view(template_name='login.html'), name='home'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
    path('register/', register, name='register'),

    # POPRAWKA: Przenosimy wszystkie główne widoki HTML aplikacji
    # do pliku 'sensors/urls.py', aby uniknąć bałaganu.
    # Poniższe linie zostaną obsłużone przez sensors.urls:
    # path('dashboard/', dashboard, name='dashboard'),
    # path('profile/', profile, name='profile'),
    # path('settings/', settings_view, name='settings'),

    # POPRAWKA: Dołącz ścieżki HTML z aplikacji 'sensors' do głównego URL
    # To sprawi, że /dashboard/, /comparison/1/ itp. będą działać.
    path('', include('sensors.urls')),
]
