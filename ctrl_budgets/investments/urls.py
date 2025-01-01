from django.urls import path

from . import views

app_name = 'investments'
urlpatterns = [
    path('', views.index, name='index'),

    path('targeted-budget/new/',
         views.targeted_budget_new,
         name='targeted_budget_new'),
    path('targeted-budget/<str:budget_id>/',
         views.targeted_budget,
         name='targeted_budget'),
    path('targeted-budget/<str:budget_id>/new-transaction/',
         views.TargetedTransactionCreateView.as_view(),
         name="targeted_transaction_create"),

    path('targeted-budget/transaction/delete/<str:pk>/',
         views.TargetedTransactionDeleteView.as_view(),
         name="targeted_transaction_confirm_delete")
]
