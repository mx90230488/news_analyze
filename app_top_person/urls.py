from django.urls import path
from app_top_person import views

# Declare a namespace for this APP
app_name = 'app_top_person'

urlpatterns = [
    # For home
    path('', views.home, name='home'),
    # For Ajax
    path('api_get_topPerson/', views.api_get_topPerson),
]
