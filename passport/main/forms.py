import re

from ajax_select.fields import AutoCompleteSelectMultipleWidget, AutoCompleteSelectWidget, AutoCompleteWidget
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Item, Order, Set, SetItem

set_item_formset = forms.inlineformset_factory(
    Set,
    SetItem,
    fields=['item', 'amount', 'tray', 'comment'],
    widgets={'item': AutoCompleteWidget('article'),
             'amount': forms.NumberInput(attrs={'style': 'max-width:100px;'}),
             'tray': forms.NumberInput(attrs={'style': 'max-width:100px;'}),
             'comment': forms.TextInput(),
             })


def modelform_init(_model, _fields='__all__'):
    """
    Create universal forms for basic models.
    Args:
        _model (): Django model
        _fields (list[str]): Optional, list of fields to display, default: all

    Returns:
        form(ModelForm)
    """
    class BasicForm(forms.ModelForm):
        class Meta:
            model = _model
            fields = _fields

        def clean(self):
            cleaned_data = super().clean()
            cleaned_data['name'] = ' '.join(cleaned_data['name'].split())
            if cleaned_data.get('article'):
                cleaned_data['article'] = cleaned_data['article'].strip().upper()
            return cleaned_data

    return BasicForm


class SetForm(forms.ModelForm):
    class Meta:
        model = Set
        fields = ['serial', 'article', 'comment']
        widgets = {
            'article': AutoCompleteWidget('article'),
        }

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['serial'] = ''.join(cleaned_data['serial'].split()).upper()
        valid_serial = re.findall(rf"^{cleaned_data['article']}-\d+$", cleaned_data['serial'])
        if not valid_serial:
            raise ValidationError({
                'serial': _('Serial number must follow the pattern [article]-[digits].')
            })
        find_serial = Set.objects.filter(serial=cleaned_data['serial'])
        if find_serial and cleaned_data['serial'] != self.instance.serial:
            raise ValidationError({
                'serial': _('A set with this serial number already exists.')
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
        fields = ['distributor', 'recipient', 'comment', 'city', 'sets']
        widgets = {
            'city': AutoCompleteSelectWidget('city'),
            'sets': AutoCompleteSelectMultipleWidget('set'),
        }


class OrderBasicForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = []
