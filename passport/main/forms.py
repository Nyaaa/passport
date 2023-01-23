from django import forms
from django.forms import modelform_factory
from .models import Item, Set, Series
from dal import autocomplete


def modelform_init(model):
    return modelform_factory(model, fields='__all__')


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['article', 'name', 'series']

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['article'] = cleaned_data['article'].upper()
        return cleaned_data


class SetForm(forms.ModelForm):
    class Meta:
        model = Set
        fields = ['serial', 'article', 'accounted', 'items']
        widgets = {
            'items': autocomplete.ModelSelect2Multiple(url='item-autocomplete'),
            'article': autocomplete.ModelSelect2(url='item-autocomplete')
        }


class SetBasicForm(forms.ModelForm):
    article = forms.ModelChoiceField(queryset=Item.objects.filter(is_set=True).order_by('article'))

    class Meta:
        model = Set
        fields = ['article']
