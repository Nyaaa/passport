from django import forms
from .models import Item, Set, Order
from dal import autocomplete
from django.core.exceptions import ValidationError


def modelform_init(model):
    return forms.modelform_factory(model, fields='__all__')


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
        fields = ['serial', 'article', 'comment']
        widgets = {
            'article': autocomplete.ModelSelect2(url='item-autocomplete'),
        }

    def clean(self):
        cleaned_data = super().clean()
        try:
            int(cleaned_data.get('serial').rsplit('-')[1])
        except ValueError:
            raise ValidationError({
                "serial": "serial must end with number"
            })
        return cleaned_data


class SetBasicForm(forms.ModelForm):
    article = forms.ModelChoiceField(queryset=Item.objects.filter(is_set=True).order_by('article'))

    class Meta:
        model = Set
        fields = ['article']


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['distributor', 'recipient', 'city', 'sets']
        widgets = {
            'city': autocomplete.ModelSelect2(url='city-autocomplete'),
            'sets': autocomplete.ModelSelect2Multiple(url='set-autocomplete'),
        }

