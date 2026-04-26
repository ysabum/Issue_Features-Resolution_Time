from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), # Home
    path('calculator/', views.calculator, name='calculator'), # MRT Calc
    path('about/', views.about, name='about'), # About
]