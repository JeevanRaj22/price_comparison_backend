# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('protected/', views.some_protected_view, name='protected'),
    path('set_session/', views.set_session,name="session_set"),
    path('get_session/', views.check_session,name="session_check"),
    path('csrf/', views.get_csrf_token, name='get_csrf_token'),
]
