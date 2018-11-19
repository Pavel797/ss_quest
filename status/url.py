from django.urls import path
from . import views

app_name = 'status'
urlpatterns = [
    path('', views.index, name='index'),
    path('get_status_json/', views.get_status_json, name='get_status_json'),
]