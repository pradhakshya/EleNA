from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search, name='search'),
    path('get_route/', views.get_route, name='get_route'),
]