from django import forms

from .models import OnlineGiving


class PublicGivingForm(forms.ModelForm):
    class Meta:
        model = OnlineGiving
        fields = ['name', 'email', 'amount', 'giving_category', 'frequency', 'note']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder': 'Full name'})
        self.fields['email'].widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder': 'you@example.com'})
        self.fields['amount'].widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder': 'Enter amount', 'min': '1', 'step': '0.01'})
        self.fields['giving_category'].widget.attrs.update({'class': 'form-select form-select-lg'})
        self.fields['frequency'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['note'].widget.attrs.update({'class': 'form-control', 'rows': 2})

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError('Amount must be greater than zero.')
        return amount