from django.views.generic import CreateView, UpdateView, DeleteView,\
    TemplateView, DetailView
from .models import Item, Set, SetItem, Order
from .tables import SetTable, table_factory, OrderTable
from .filters import ItemFilter, SetFilter, filter_factory, OrderFilter
from .forms import SetForm, SetBasicForm, modelform_init, ItemForm, OrderForm, set_item_formset
from django_filters.views import FilterView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from collections import defaultdict
from django.db.models import OuterRef, Subquery


# Create your views here.
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'


class CommonUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'common_edit.html'

    def __init__(self, *args, **kwargs):
        super(CommonUpdate, self).__init__(*args, **kwargs)
        self.form_class = modelform_init(self.model)
        self.success_url = reverse_lazy(self.model.__name__.lower())


class CommonListView(LoginRequiredMixin, FilterView):
    template_name = 'common_list.html'
    paginate_by = 20
    ordering = 'name'

    def __init__(self, *args, **kwargs):
        super(CommonListView, self).__init__(*args, **kwargs)
        self.filterset_class = filter_factory(self.model)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['edit_url'] = f'{self.model.__name__.lower()}_edit'
        context['delete_url'] = f'{self.model.__name__.lower()}_delete'
        context['query_string'] = self.request.GET.urlencode()
        return context


class CommonDelete(LoginRequiredMixin, DeleteView):
    template_name = 'common_delete.html'

    def __init__(self, *args, **kwargs):
        super(CommonDelete, self).__init__(*args, **kwargs)
        self.success_url = reverse_lazy(self.model.__name__.lower())


class CommonCreateView(LoginRequiredMixin, CreateView):
    # TODO implement this
    # strip spaces
    # capitalize
    pass


class SetListView(CommonListView):
    model = Set
    ordering = 'serial'
    template_name = 'set_list.html'

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
        myd = {context['sets'][0].serial: _dict}
        context['set_items'] = myd
        return context


class SetCreateView(LoginRequiredMixin, CreateView):
    model = Set
    template_name = 'set_edit.html'
    form_class = SetForm


class ItemListView(CommonListView):
    ordering = 'article'

    def __init__(self, *args, **kwargs):
        super(ItemListView, self).__init__(*args, **kwargs)
        self.model = Item
        self.filterset_class = ItemFilter

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('series')
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


class OrderListView(CommonListView):
    template_name = 'order_list.html'

    def __init__(self, *args, **kwargs):
        super(OrderListView, self).__init__(*args, **kwargs)
        self.model = Order
        self.form_class = OrderForm
        self.filterset_class = OrderFilter
        self.table_class = OrderTable
        self.object_list = self.model.objects.all()

    def form_valid(self, form):
        _order = form.save(commit=False)
        response = super().form_valid(form)
        return response

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('distributor', 'recipient', 'city')
        qs = qs.prefetch_related('sets')
        qs = qs.order_by('-date')
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
        print(sets_items)

        return context
