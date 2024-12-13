from django.urls import path

from . import views

app_name = 'investments'
urlpatterns = [
    path('', views.index, name='index'),
    path('targeted-budget/new/', views.targeted_budget_new, name='targeted_budget_new'),
    path('targeted-budget/<str:budget_id>/', views.targeted_budget, name='targeted_budget'),
]
