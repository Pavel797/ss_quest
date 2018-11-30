from django.urls import path
from . import views

app_name = 'quest_api'
urlpatterns = [
    path('get_markers/', views.get_markers, name='get_markers'),
    path('take_marker/', views.take_marker, name='take_marker'),
    path('get_hints/', views.get_hints, name='get_hints'),
    #path('drop_markers/', views.drop_markers, name='drop_markers'),
    path('set_my_position/', views.set_my_position, name='set_my_position'),
    path('create_prod_base/', views.create_prod_base, name='create_prod_base'),
]