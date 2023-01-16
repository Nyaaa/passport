from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Item
from .tables import ItemTable
from .filters import ItemFilter
from django_tables2 import SingleTableView
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
