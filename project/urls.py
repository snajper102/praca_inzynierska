from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.authtoken import views as drf_views
from sensors.views import dashboard  # Import widoku dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-token-auth/', drf_views.obtain_auth_token, name='api-token-auth'),
    path('api/', include('sensors.urls')),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
    path('dashboard/', dashboard, name='dashboard'),  # Dodana ścieżka dla dashboardu
]
