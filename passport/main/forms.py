from django import forms
from .models import Item, Series


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['article', 'name']


class SeriesForm(forms.ModelForm):
    class Meta:
        model = Series
        fields = ['name']

