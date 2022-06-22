from django.urls import path
from app_pk_company import views

app_name='app_pk_company'

urlpatterns = [
    path('', views.home, name='home'),
    path('api_get_taipei_mayor_data/', views.api_get_taipei_mayor_data),
]