from django.views.generic import CreateView, UpdateView, DeleteView, TemplateView
from .models import Item, Set
from .tables import SetTable, table_factory
from .filters import ItemFilter, SetFilter, filter_factory
from .forms import SetForm, modelform_init
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2.export.views import ExportMixin
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.
class ItemListView(LoginRequiredMixin, ExportMixin, SingleTableMixin, CreateView, FilterView):
    model = Item
    ordering = 'article'
    template_name = 'common_list_edit.html'
    table_class = table_factory(Item, 'item')
    filterset_class = ItemFilter
    form_class = modelform_init(model=model, fields=('article', 'name'))
    success_url = '/item/'


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'


class CommonUpdate(LoginRequiredMixin, UpdateView):
    def __init__(self, *args, **kwargs):
        super(CommonUpdate, self).__init__(*args, **kwargs)
        text = self.model.__name__.lower()
        self.form_class = modelform_init(self.model)
        self.template_name = 'common_edit.html'
        self.success_url = f'/{text}/'


class CommonDelete(LoginRequiredMixin, DeleteView):  # FIXME: doesn't delete, response 200
    def __init__(self, *args, **kwargs):
        super(CommonDelete, self).__init__(*args, **kwargs)
        text = self.model.__name__.lower()
        self.form_class = modelform_init(self.model)
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


class SetListView(LoginRequiredMixin, ExportMixin, SingleTableMixin, FilterView):
    model = Set
    ordering = 'serial'
    template_name = 'common_list_edit.html'
    table_class = SetTable
    filterset_class = SetFilter


class SetUpdateView(LoginRequiredMixin, UpdateView):
    model = Set
    template_name = 'set_edit.html'
    form_class = SetForm
    success_url = '/sets/'
