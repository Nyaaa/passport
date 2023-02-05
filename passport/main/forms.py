from django import forms
from .models import Item, Set, Order, SetItem
from django.core.exceptions import ValidationError
from ajax_select.fields import AutoCompleteSelectField, AutoCompleteSelectMultipleField, \
    AutoCompleteWidget, AutoCompleteSelectWidget, AutoCompleteSelectMultipleWidget


set_item_formset = forms.inlineformset_factory(Set, SetItem,
                                               fields=['item', 'amount', 'tray', 'comment'],
                                               widgets={'item': AutoCompleteWidget('article', attrs={'class': 'form-control'}),
                                                        'amount': forms.NumberInput(attrs={'class': 'form-control'}),
                                                        'tray': forms.NumberInput(attrs={'class': 'form-control'}),
                                                        'comment': forms.TextInput(attrs={'class': 'form-control'}),
                                                        })


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
            'article': AutoCompleteWidget('article'),
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
            'city': AutoCompleteSelectWidget('city'),
            'sets': AutoCompleteSelectMultipleWidget('set'),
        }

