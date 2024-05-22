from django import forms

class BalanceUpdateForm(forms.Form):
    date = forms.DateField(
        label='Date',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    available_balance = forms.DecimalField(
        label='Available Balance',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

class DateRangeForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    
class InventoryForm(forms.Form):
    start_inventory = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
    end_inventory = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
