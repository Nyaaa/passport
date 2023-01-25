from django.views.generic import CreateView, UpdateView, DeleteView, TemplateView, DetailView
from .models import Item, Set, SetItem
from .tables import SetTable, table_factory
from .filters import ItemFilter, SetFilter, filter_factory
from .forms import SetForm, SetBasicForm, modelform_init, ItemForm
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2.export.views import ExportMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from dal import autocomplete
from django.shortcuts import render
from django import forms
from collections import defaultdict


# Create your views here.
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'


class CommonUpdate(LoginRequiredMixin, UpdateView):
    def __init__(self, *args, **kwargs):
        super(CommonUpdate, self).__init__(*args, **kwargs)
        text = self.model.__name__.lower()
        self.form_class = modelform_init(self.model)
        self.template_name = 'common_edit.html'
        self.success_url = f'/{text}/'


class CommonDelete(LoginRequiredMixin, DeleteView):
    def __init__(self, *args, **kwargs):
        super(CommonDelete, self).__init__(*args, **kwargs)
        text = self.model.__name__.lower()
        self.template_name = 'common_delete.html'
        self.success_url = f'/{text}/'


class CommonListCreate(LoginRequiredMixin, ExportMixin, SingleTableMixin, CreateView, FilterView):
    def __init__(self, *args, **kwargs):
        super(CommonListCreate, self).__init__(*args, **kwargs)
        text = self.model.__name__.lower()
        self.template_name = "common_list_edit.html"
        self.table_class = table_factory(self.model, text)
        self.form_class = modelform_init(self.model)
        self.success_url = f'/{text}/'
        self.filterset_class = filter_factory(self.model)
        self.object_list = self.model.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.model.__name__
        return context


class SetListView(CommonListCreate):
    model = Set
    ordering = 'serial'
    template_name = 'common_list_edit.html'

    def __init__(self, *args, **kwargs):
        super(SetListView, self).__init__(*args, **kwargs)
        self.form_class = SetBasicForm
        self.filterset_class = SetFilter
        self.table_class = SetTable

    def form_valid(self, form):
        _set = form.save(commit=False)
        prev = Set.objects.filter(article=_set.article).order_by('pk').last()
        prev_items = None
        if prev:
            # setting serial number
            prev_serial = int(prev.pk.split('-')[1])
            next_serial = f"{_set.article}-{(prev_serial + 1):04d}"
            prev_items = list(SetItem.objects.filter(set=prev.pk))
        else:
            next_serial = f"{_set.article}-{1:04d}"
        _set.serial = next_serial

        # copying m2m items
        if prev_items:
            _set.save()
            copy_items = [SetItem(set=_set, item=item.item, amount=item.amount, tray=item.tray) for item in prev_items]
            SetItem.objects.bulk_create(copy_items)

        response = super().form_valid(form)
        return response


class SetDetailView(LoginRequiredMixin, DetailView):
    model = Set
    template_name = 'set_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        _dict = defaultdict(list)
        items = SetItem.objects.filter(set=self.get_object())
        for i in items:
            _dict[i.tray].append(i)
        context["set_items"] = _dict
        return context


class SetCreateView(LoginRequiredMixin, CreateView):
    model = Set
    template_name = 'set_edit.html'
    form_class = SetForm
    success_url = '/set/'


class ItemListView(CommonListCreate):
    def __init__(self, *args, **kwargs):
        super(CommonListCreate, self).__init__(*args, **kwargs)
        self.model = Item
        self.ordering = 'article'
        self.template_name = 'common_list_edit.html'
        self.table_class = table_factory(Item, 'item')
        self.filterset_class = ItemFilter
        self.form_class = ItemForm
        self.success_url = '/item/'
        self.object_list = self.model.objects.all()


class ItemAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Item.objects.all()
        if self.q:
            qs = qs.filter(article__istartswith=self.q)
        return qs


def set_items(request, pk):
    _set = Set.objects.get(serial=pk)
    form = SetForm(instance=_set)
    set_item_formset = forms.inlineformset_factory(Set,
                                                   SetItem,
                                                   fields=['item', 'amount', 'tray', 'comment'],
                                                   widgets={'item': autocomplete.ModelSelect2(url='item-autocomplete'),
                                                            'comment': forms.TextInput
                                                            })

    if request.method == 'POST':
        formset = set_item_formset(request.POST, instance=_set)
        if formset.is_valid():
            formset.save()

    formset = set_item_formset(instance=_set)
    return render(request, 'set_edit.html', {'formset': formset, 'form': form})
