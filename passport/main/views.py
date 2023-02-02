from django.views.generic import CreateView, UpdateView, DeleteView, TemplateView, DetailView
from .models import Item, Set, SetItem, Order, City
from .tables import SetTable, table_factory, OrderTable
from .filters import ItemFilter, SetFilter, filter_factory, OrderFilter
from .forms import SetForm, SetBasicForm, modelform_init, ItemForm, OrderForm, set_item_formset
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2.export.views import ExportMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from dal import autocomplete
from django.shortcuts import render
from django.urls import reverse_lazy
from collections import defaultdict


# Create your views here.
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'


class CommonUpdate(LoginRequiredMixin, UpdateView):
    text = None
    template_name = 'common_edit.html'

    def __init__(self, *args, **kwargs):
        super(CommonUpdate, self).__init__(*args, **kwargs)
        self.form_class = modelform_init(self.model)
        self.success_url = reverse_lazy(f'{self.text}')


class CommonDelete(LoginRequiredMixin, DeleteView):
    text = None
    template_name = 'common_delete.html'

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy(self.text, args=[self.kwargs['slug']])


class CommonListCreate(LoginRequiredMixin, ExportMixin, SingleTableMixin, CreateView, FilterView):
    text = None
    template_name = "common_list_edit.html"

    def __init__(self, *args, **kwargs):
        super(CommonListCreate, self).__init__(*args, **kwargs)
        self.table_class = table_factory(self.model, self.text)
        self.form_class = modelform_init(self.model)
        self.success_url = reverse_lazy(f'{self.text}')
        self.filterset_class = filter_factory(self.model)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.model.__name__
        return context


class SetListView(CommonListCreate):
    model = Set
    ordering = 'serial'

    def __init__(self, *args, **kwargs):
        super(SetListView, self).__init__(*args, **kwargs)
        self.form_class = SetBasicForm
        self.filterset_class = SetFilter
        self.table_class = SetTable

    def form_valid(self, form):
        _set = form.save(commit=False)
        article = str(_set.article).replace('USED-', '')
        prev = Set.objects.filter(article=article).order_by('pk').last()
        prev_items = None
        if prev:
            # setting serial number
            prev_serial = int(prev.pk.split('-')[1])
            next_serial = f"{article}-{(prev_serial + 1):04d}"
            prev_items = list(SetItem.objects.filter(set=prev.pk))
        else:
            next_serial = f"{article}-{1:04d}"
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
        items = SetItem.objects.filter(set=self.get_object()).select_related('item')
        for i in items:
            _dict[i.tray].append(i)
        context['set_items'] = _dict
        return context


class SetCreateView(LoginRequiredMixin, CreateView):
    model = Set
    template_name = 'set_edit.html'
    form_class = SetForm
    success_url = reverse_lazy('set')


class ItemListView(CommonListCreate):
    ordering = 'article'

    def __init__(self, *args, **kwargs):
        super(CommonListCreate, self).__init__(*args, **kwargs)
        self.model = Item
        self.table_class = table_factory(Item, 'item')
        self.filterset_class = ItemFilter
        self.form_class = ItemForm
        self.success_url = reverse_lazy('item')


class ItemAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Item.objects.all()
        if self.q:
            qs = qs.filter(article__icontains=self.q)
        return qs


class SetAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Set.objects.all()
        if self.q:
            qs = qs.filter(serial__icontains=self.q)
        return qs


class SetUpdateView(LoginRequiredMixin, UpdateView):
    model = Set
    template_name = 'set_edit.html'
    form_class = SetForm
    success_url = reverse_lazy('set')

    def get(self, request, *args, **kwargs):
        _set = Set.objects.get(serial=self.get_object())
        form = SetForm(instance=_set)
        formset = set_item_formset(instance=_set)
        return render(request, 'set_edit.html', {'formset': formset, 'form': form})

    def post(self, request, *args, **kwargs):
        _set = Set.objects.get(serial=self.get_object())
        if request.POST.get('serial'):
            form = SetForm(request.POST, instance=_set)
            if form.is_valid():
                form.save()

        formset = set_item_formset(request.POST, instance=_set)
        if formset.is_valid():
            formset.save()

        form = SetForm(instance=_set)
        formset = set_item_formset(instance=_set)
        return render(request, 'set_edit.html', {'formset': formset, 'form': form})


class OrderListView(CommonListCreate):
    template_name = 'order_list_create.html'

    def __init__(self, *args, **kwargs):
        super(CommonListCreate, self).__init__(*args, **kwargs)
        self.model = Order
        self.form_class = OrderForm
        self.filterset_class = OrderFilter
        self.table_class = OrderTable
        self.success_url = reverse_lazy('order')

    def form_valid(self, form):
        _order = form.save(commit=False)
        response = super().form_valid(form)
        return response

    def get_queryset(self):
        """This fixes N+1 problem created by django-tables"""
        qs = super().get_queryset()
        qs = qs.select_related('distributor', 'recipient', 'city')
        qs = qs.prefetch_related('sets')
        qs = qs.order_by('-date')
        return qs


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'order_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sets = self.get_object().sets.all()
        sets_items = dict()
        for i in sets:
            _dict = defaultdict(list)
            items = SetItem.objects.filter(set=i).select_related('item')
            for j in items:
                _dict[j.tray].append(j)
            sets_items[i.serial] = _dict
        context['full_list'] = sets_items

        return context
