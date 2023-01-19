from django import forms
from django.forms import modelform_factory
from .models import Item, Set


def modelform_init(model, fields=('name',)):
    return modelform_factory(model, fields=fields)


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['article', 'name']

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['article'] = cleaned_data['article'].upper()
        return cleaned_data



class SetForm(forms.ModelForm):
    set_article = forms.ModelChoiceField(queryset=Item.objects.all().order_by('article'))
    items = forms.ModelMultipleChoiceField(queryset=Item.objects.all().order_by('article'), widget=forms.SelectMultiple)

    class Meta:
        model = Set
        fields = ['serial', 'set_article', 'accounted', 'series', 'items']
