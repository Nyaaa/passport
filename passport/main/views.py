from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Item, Series
from .tables import ItemTable
from .filters import ItemFilter
from .forms import ItemForm, SeriesForm
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2.export.views import ExportMixin


# Create your views here.
class ItemListView(ExportMixin, SingleTableMixin, FilterView):
    model = Item
    ordering = 'article'
    template_name = 'items.html'
    table_class = ItemTable
    filterset_class = ItemFilter


class HomeView(TemplateView):
    template_name = 'home.html'


class ItemUpdate(UpdateView):
    form_class = ItemForm
    model = Item
    template_name = 'item_edit.html'
    success_url = '/items/'


class ListAndCreate(CreateView):
    model = Series
    template_name = "generic_list_edit.html"
    form_class = SeriesForm
    success_url = '/series/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["objects"] = self.model.objects.all()
        return context
