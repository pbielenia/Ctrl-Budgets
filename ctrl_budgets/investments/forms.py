from django import forms
from .models import Portfolio


class CreatePortfolioForm(forms.Form):
    name = forms.CharField(label="Name", max_length=80)
