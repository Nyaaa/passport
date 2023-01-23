from django.views.generic import CreateView, UpdateView, DeleteView, TemplateView
from .models import Item, Set
from .tables import SetTable, table_factory
from .filters import ItemFilter, SetFilter, filter_factory
from .forms import SetForm, SetBasicForm, modelform_init, ItemForm
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2.export.views import ExportMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from dal import autocomplete


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
    table_class = SetTable

    def __init__(self, *args, **kwargs):
        super(SetListView, self).__init__(*args, **kwargs)
        self.form_class = SetBasicForm
        self.filterset_class = SetFilter


class SetUpdateView(LoginRequiredMixin, UpdateView):
    model = Set
    template_name = 'set_edit.html'
    form_class = SetForm
    success_url = '/sets/'


class SetCreateView(LoginRequiredMixin, CreateView):
    model = Set
    template_name = 'set_edit.html'
    form_class = SetForm
    success_url = '/sets/'


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
