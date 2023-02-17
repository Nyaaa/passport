from django.views.generic import UpdateView, DeleteView, TemplateView,\
    DetailView, FormView, ListView
from .models import Item, Set, SetItem, Order
from .tables import SetTable, table_factory, OrderTable
from .filters import ItemFilter, SetFilter, filter_factory, OrderFilter
from .forms import SetForm, SetBasicForm, modelform_init, OrderForm, set_item_formset
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2.export.views import ExportMixin
from django_tables2 import RequestConfig
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from collections import defaultdict
from django.db.models import OuterRef, Subquery, Count, ProtectedError, RestrictedError
from django.db.models.functions import TruncYear
from django.utils import timezone
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin


# Create your views here.
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = Set.objects.all()
        latest_order = Order.objects.filter(sets=OuterRef('pk')).order_by('-date')[:1]
        self.qs = qs.prefetch_related('order_set').annotate(
            distributor=Subquery(latest_order.values('distributor__name')),
            date=Subquery(latest_order.values('date')),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date_limit = timezone.now() - timezone.timedelta(days=5*365)

        context['distributor_sets_chart'] = self.qs.values('distributor').order_by('distributor')\
            .annotate(count=Count('serial')).values('distributor', 'count')

        context['shipments_by_year'] = Order.objects.exclude(distributor__pk=1)\
            .annotate(year=TruncYear('date')).values('year').annotate(count=Count('date'))\
            .values('year', 'count').filter(year__gt=date_limit)

        context['returns'] = Order.objects.filter(distributor__pk=1)\
            .annotate(year=TruncYear('date')).values('year').annotate(count=Count('date'))\
            .values('year', 'count').filter(year__gt=date_limit)
        return context


class CommonUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    template_name = "common_edit.html"
    success_message = '%(name)s updated successfully'

    def __init__(self, *args, **kwargs):
        super(CommonUpdateView, self).__init__(*args, **kwargs)
        if self.model == Set:
            self.form_class = SetForm
        else:
            self.form_class = modelform_init(self.model)
        self.text = self.model.__name__.lower()

    def get_success_url(self):
        return f'{reverse_lazy(self.text)}?{self.request.GET.urlencode()}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit {self.text}'
        return context


class CommonListView(LoginRequiredMixin, ExportMixin, SingleTableMixin, FilterView, FormView):
    template_name = 'common_list.html'
    paginate_by = 20
    ordering = 'name'

    def __init__(self, *args, **kwargs):
        super(CommonListView, self).__init__(*args, **kwargs)
        self.text = self.model.__name__.lower()
        self.form_class = modelform_init(self.model)
        self.table_class = table_factory(self.model)
        self.filterset_class = filter_factory(self.model)
        self.form_class = modelform_init(self.model)
        self.object_list = self.get_queryset()

    def form_valid(self, form):
        obj = form.save()
        messages.success(self.request, f'"{obj}" created successfully')
        return super(CommonListView, self).form_valid(form)

    def get_success_url(self):
        return f'{reverse_lazy(self.text)}?{self.request.GET.urlencode()}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'{self.model.__name__}'
        return context

    def get_table(self, **kwargs):
        table = self.table_class(data=self.get_table_data(), request=self.request, **kwargs)
        table.request = self.request
        return RequestConfig(self.request, paginate=self.get_table_pagination(table)).configure(table)


class CommonDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'common_delete.html'

    def __init__(self, *args, **kwargs):
        super(CommonDeleteView, self).__init__(*args, **kwargs)
        self.success_url = reverse_lazy(self.model.__name__.lower())

    def form_valid(self, *args, **kwargs):
        obj = self.get_object()
        try:
            super(CommonDeleteView, self).delete(*args, **kwargs)
            messages.success(self.request, f'"{obj}" deleted successfully')
        except (ProtectedError, RestrictedError) as e:
            messages.error(self.request, e.args[0])
        return redirect(self.success_url)


class ItemListView(CommonListView):
    model = Item
    ordering = 'article'

    def __init__(self, *args, **kwargs):
        super(ItemListView, self).__init__(*args, **kwargs)
        self.filterset_class = ItemFilter

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('series')
        return qs


class SetListView(CommonListView):
    model = Set
    ordering = 'serial'

    def __init__(self, *args, **kwargs):
        super(SetListView, self).__init__(*args, **kwargs)
        self.filterset_class = SetFilter
        self.table_class = SetTable
        self.form_class = SetBasicForm

    def form_valid(self, form):
        _set = form.save(commit=False)
        article = str(_set.article).replace('USED-', '')
        prev = Set.objects.filter(article=article).order_by('pk').last()
        prev_items = None
        # setting serial number
        if prev:
            prev_serial = int(prev.pk.split('-')[1])
            next_serial = f"{article}-{(prev_serial + 1):04d}"
            prev_items = list(SetItem.objects.filter(set=prev.pk))
        else:
            next_serial = f"{article}-{1:04d}"
        _set.serial = next_serial

        # copying m2m items
        _set.save()
        if prev_items:
            copy_items = [SetItem(set=_set, item=item.item, amount=item.amount, tray=item.tray) for item in prev_items]
            SetItem.objects.bulk_create(copy_items)

        self.success_url = reverse('item')
        return super().form_valid(form)

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('article')
        latest_order = Order.objects.filter(sets=OuterRef('pk')).order_by('-date')[:1]
        qs = qs.prefetch_related('order_set').annotate(recipient=Subquery(latest_order.values('recipient__name')),
                                                       distributor=Subquery(latest_order.values('distributor__name')),
                                                       city=Subquery(latest_order.values('city__name')),
                                                       date=Subquery(latest_order.values('date')),
                                                       document=Subquery(latest_order.values('document')))
        return qs


class SetDetailView(LoginRequiredMixin, DetailView):
    model = Set
    template_name = 'set_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sets'] = [self.get_object()]
        _dict = defaultdict(list)
        items = SetItem.objects.filter(set=self.get_object()).select_related('item')
        for i in items:
            _dict[i.tray].append(i)
        context['set_items'] = {context['sets'][0].serial: _dict}
        context['order'] = Order.objects.filter(sets=context['sets'][0]).order_by('-date').first()
        return context


class SetUpdateView(LoginRequiredMixin, UpdateView):
    model = Set
    template_name = 'set_edit.html'
    form_class = SetForm
    success_url = reverse_lazy('set')

    def get(self, request, *args, **kwargs):
        _set = Set.objects.get(serial=self.get_object())
        form = SetForm(instance=_set)
        formset = set_item_formset(instance=_set)
        return render(request, self.template_name, {'formset': formset, 'form': form})

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
        return render(request, self.template_name, {'formset': formset, 'form': form})


class OrderListView(CommonListView):
    model = Order
    ordering = '-date'

    def __init__(self, *args, **kwargs):
        super(OrderListView, self).__init__(*args, **kwargs)
        self.filterset_class = OrderFilter
        self.object_list = self.model.objects.all()
        self.table_class = OrderTable
        self.form_class = OrderForm

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('distributor', 'recipient', 'city')
        qs = qs.prefetch_related('sets')
        return qs


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'set_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sets'] = self.get_object().sets.all()
        sets_items = dict()
        for i in context['sets']:
            _dict = defaultdict(list)
            items = SetItem.objects.filter(set=i).select_related('item')
            for j in items:
                _dict[j.tray].append(j)
            sets_items[i.serial] = _dict
        context['set_items'] = sets_items

        return context


class OrderUpdateView(CommonUpdateView):
    model = Order
    template_name = 'common_edit.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_class = OrderForm
        self.text = self.model.__name__.lower()
        self.success_url = reverse_lazy(self.text)


class IncompleteSetView(LoginRequiredMixin, ListView):
    model = Set
    template_name = 'incomplete.html'

    def get_queryset(self):
        qs = super().get_queryset()
        latest_order = Order.objects.filter(sets=OuterRef('pk')).order_by('-date')[:1]
        sets = qs.prefetch_related('order_set').annotate(
            recipient=Subquery(latest_order.values('recipient__pk'))).filter(recipient=1)
        qs = SetItem.objects.select_related().filter(set__in=sets).values('item', 'amount', 'comment', 'set')

        return qs
