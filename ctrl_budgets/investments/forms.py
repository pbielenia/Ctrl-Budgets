from django import forms
from .models import TargetedTransaction


class CreatePortfolioForm(forms.Form):
    name = forms.CharField(label="Name", max_length=80)


class ChangeTargetedBudgetsVaultValueForm(forms.Form):
    value = forms.IntegerField(min_value=5, step_size=5)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['value'].widget.attrs.update({'class': 'form-input'})


class NewTargetedTransactionForm(forms.Form):
    date = forms.DateField(label="Date")
    type = forms.ChoiceField(label="Type", choices=TargetedTransaction.TYPE_CHOICES)
    cost = forms.IntegerField(min_value=5, step_size=5)
    description = forms.CharField(max_length=300, strip=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs.update({'class': 'form-input'})
        self.fields['type'].widget.attrs.update({'class': 'form-input'})
        self.fields['cost'].widget.attrs.update({'class': 'form-input'})
        self.fields['description'].widget.attrs.update({'class': 'form-input'})
