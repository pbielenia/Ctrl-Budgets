from django.urls import path

from . import views

app_name = 'investments'
urlpatterns = [
    path('', views.index, name='index'),
    path('portfolio/new/', views.new_portfolio, name='new_portfolio'),
    path('portfolio/<str:pk>/', views.portfolio, name='portfolio'),
    path('portfolio/<str:portfolio_id>/asset-class/<str:asset_type_id>',
         views.portfolio_element, name='portfolio_element'),
    path('targeted-budget/new/', views.targeted_budget_new, name='targeted_budget_new'),
    path('targeted-budget/<str:budget_id>/', views.targeted_budget, name='targeted_budget'),
]
