from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.authtoken import views as drf_views
from sensors.views import dashboard, register, profile

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API Authentication
    path('api-token-auth/', drf_views.obtain_auth_token, name='api-token-auth'),
    path('api/', include('sensors.urls')),

    # User Authentication
    path('', LoginView.as_view(template_name='login.html'), name='home'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
    path('register/', register, name='register'),

    # Dashboard & Profile
    path('dashboard/', dashboard, name='dashboard'),
    path('profile/', profile, name='profile'),
]