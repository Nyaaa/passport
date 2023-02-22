from django import forms
from .models import Item, Set, Order, SetItem
from django.core.exceptions import ValidationError
from ajax_select.fields import AutoCompleteWidget, AutoCompleteSelectWidget, AutoCompleteSelectMultipleWidget

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
        cleaned_data['serial'] = cleaned_data['serial'].strip().upper()
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
        fields = ['distributor', 'recipient', 'comment', 'city', 'sets']
        widgets = {
            'city': AutoCompleteSelectWidget('city'),
            'sets': AutoCompleteSelectMultipleWidget('set'),
        }


class OrderBasicForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ['distributor', 'recipient', 'city', 'sets', 'date', 'comment', 'document']
