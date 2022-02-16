from django.urls import path
from . import views

urlpatterns = [
    path('', views.savings, name='savings'),
    path('budget/', views.budget, name='budget')
]
