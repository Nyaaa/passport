from django.views.generic import UpdateView, DeleteView, TemplateView,\
    DetailView, FormView, ListView, CreateView
from .models import Item, Set, SetItem, Order
from .tables import SetTable, table_factory, OrderTable
from .filters import ItemFilter, SetFilter, filter_factory, OrderFilter
from .forms import SetForm, SetBasicForm, modelform_init, OrderForm, set_item_formset, OrderBasicForm
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2.export.views import ExportMixin
from django_tables2 import RequestConfig
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from collections import defaultdict
from django.db.models import OuterRef, Subquery, Count, ProtectedError, RestrictedError
from django.db.models.functions import TruncYear
from django.utils import timezone
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin


# Create your views here.
class HomeView(LoginRequiredMixin, TemplateView):
    """Dashboard / home page"""
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        """Data prep for displaying charts"""
        context = super().get_context_data(**kwargs)
        date_limit = timezone.now() - timezone.timedelta(days=5*365)
        qs = Set.objects.all()
        latest_order = Order.objects.filter(sets=OuterRef('pk')).order_by('-date')[:1]
        qs = qs.prefetch_related('order_set').annotate(
            distributor=Subquery(latest_order.values('distributor__name')),
            date=Subquery(latest_order.values('date')),
        )

        context['distributor_sets_chart'] = qs.values('distributor').order_by('distributor')\
            .annotate(count=Count('serial')).values('distributor', 'count')

        context['shipments'] = Order.objects.exclude(distributor__pk=1)\
            .annotate(year=TruncYear('date')).values('year')\
            .annotate(Count('date', distinct=True), Count('sets'))\
            .values('year', 'date__count', 'sets__count').filter(year__gt=date_limit)

        context['returns'] = Order.objects.filter(distributor__pk=1)\
            .annotate(year=TruncYear('date')).values('year')\
            .annotate(Count('date', distinct=True), Count('sets'))\
            .values('year', 'date__count', 'sets__count').filter(year__gt=date_limit)

        return context


class CommonUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    """Universal UpdateView for all basic models"""
    template_name = "common_edit.html"

    def __init__(self, *args, **kwargs):
        """
        Gets model from urls.py
        Args:
            **kwargs (): model: Django model
        """
        super(CommonUpdateView, self).__init__(*args, **kwargs)
        self.form_class = modelform_init(self.model)
        self.text = self.model.__name__.lower()

    def get_success_message(self, cleaned_data):
        return f'{self.object} updated successfully'

    def get_success_url(self):
        return f'{reverse_lazy(self.text)}?{self.request.GET.urlencode()}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit {self.text}'
        context['delete_view'] = reverse_lazy(f'{self.text}_delete', kwargs={'pk': self.object.pk})
        return context


class CommonListView(SuccessMessageMixin, LoginRequiredMixin, ExportMixin, SingleTableMixin, FilterView, FormView):
    """Main ListView class, also used for creation instead of CreateView"""
    template_name = 'common_list.html'
    paginate_by = 20
    ordering = 'name'

    def __init__(self, *args, **kwargs):
        """
        Gets model from urls.py
        Args:
            **kwargs (): model: Django model
        """
        super(CommonListView, self).__init__(*args, **kwargs)
        self.text = self.model.__name__.lower()
        self.form_class = modelform_init(self.model)
        self.table_class = table_factory(self.model)
        self.filterset_class = filter_factory(self.model)
        self.form_class = modelform_init(self.model)
        self.object_list = self.get_queryset()
        self.object = None

    def form_valid(self, form):
        """Creates new objects in lieu of CreateView"""
        self.object = form.save()
        return super(CommonListView, self).form_valid(form)

    def get_success_url(self):
        return f'{reverse_lazy(self.text)}?{self.request.GET.urlencode()}'

    def get_success_message(self, cleaned_data):
        return f'{self.object} created successfully'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'{self.model.__name__}'
        return context

    def get_table(self, **kwargs):
        """Pass request to django-tables2 for getting query string, see tables.table_factory"""
        table = self.table_class(data=self.get_table_data(), request=self.request, **kwargs)
        table.request = self.request
        return RequestConfig(self.request, paginate=self.get_table_pagination(table)).configure(table)


class CommonDeleteView(LoginRequiredMixin, DeleteView):
    """Universal UpdateView for all models"""
    template_name = 'common_delete.html'

    def __init__(self, *args, **kwargs):
        """
        Gets model from urls.py
        Args:
            **kwargs (): model: Django model
        """
        super(CommonDeleteView, self).__init__(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(self.model.__name__.lower()) + '?' + self.request.GET.urlencode()

    def form_valid(self, *args, **kwargs):
        obj = self.get_object()
        try:
            super(CommonDeleteView, self).delete(*args, **kwargs)
            messages.success(self.request, f'{obj} deleted successfully')
        except (ProtectedError, RestrictedError) as e:
            messages.error(self.request, e.args[0])
        return redirect(self.get_success_url())


class ItemListView(CommonListView):
    model = Item
    ordering = 'article'

    def __init__(self, *args, **kwargs):
        super(ItemListView, self).__init__(*args, **kwargs)
        self.filterset_class = ItemFilter
        self.form_class = modelform_init(Item, ['article', 'name'])

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('series')
        return qs

    def get_success_url(self):
        return f'{self.object.get_absolute_url()}?{self.request.GET.urlencode()}'


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

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('set_detail', kwargs={'pk': self.object.pk})

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
        obj = self.get_object()
        context['sets'] = [obj]
        _dict = defaultdict(list)
        items = SetItem.objects.filter(set=obj).select_related('item')
        for i in items:
            _dict[i.tray].append(i)
        context['set_items'] = {context['sets'][0].serial: _dict}
        context['order'] = Order.objects.select_related().filter(sets=context['sets'][0]).order_by('-date').first()
        return context


class SetUpdateView(CommonUpdateView):
    model = Set
    template_name = 'common_edit.html'

    def __init__(self, *args, **kwargs):
        super(SetUpdateView, self).__init__(*args, **kwargs)
        self.form_class = SetForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        _set = Set.objects.get(serial=self.get_object())
        context['formset'] = set_item_formset(instance=_set)
        return context

    def form_valid(self, form):
        _set = form.save(commit=False)
        if form.is_valid():
            _set.save()
        formset = set_item_formset(self.request.POST, instance=_set)
        if formset.is_valid():
            formset.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('set_edit', kwargs={'pk': self.object.pk})


class OrderListView(CommonListView):
    model = Order
    ordering = '-date'

    def __init__(self, *args, **kwargs):
        super(OrderListView, self).__init__(*args, **kwargs)
        self.filterset_class = OrderFilter
        self.object_list = self.model.objects.all()
        self.table_class = OrderTable
        self.form_class = OrderBasicForm

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('distributor', 'recipient', 'city')
        qs = qs.prefetch_related('sets')
        return qs

    def form_valid(self, form):
        return redirect(reverse_lazy('order_create'))


class OrderCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Order
    template_name = 'common_edit.html'
    form_class = OrderForm

    def get_success_url(self):
        return reverse_lazy('order_detail', kwargs={'pk': self.object.pk})

    def get_success_message(self, _):
        return f'Order №{self.object} created successfully'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Create new order:'
        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'set_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context['sets'] = obj.sets.all().select_related().prefetch_related()
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_class = OrderForm
        self.text = self.model.__name__.lower()
        self.success_url = reverse_lazy(self.text)

    def get_success_message(self, _):
        return f'Order {self.object} updated successfully'


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
