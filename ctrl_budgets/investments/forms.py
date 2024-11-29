from django import forms
from .models import TargetedTransaction


class CreatePortfolioForm(forms.Form):
    name = forms.CharField(label="Name", max_length=80)


class NewTargetedTransactionForm(forms.Form):
    date = forms.DateField(label="Date")
    type = forms.ChoiceField(label="Type", choices=TargetedTransaction.TYPE_CHOICES)
    cost = forms.IntegerField(min_value=5, step_size=5)
    description = forms.CharField(max_length=300, strip=True)
