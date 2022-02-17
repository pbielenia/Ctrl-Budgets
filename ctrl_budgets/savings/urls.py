from django.urls import path
from . import views

urlpatterns = [
    path('', views.savings, name='savings'),
    path('budget/<str:pk>/', views.budget, name='budget')
]
