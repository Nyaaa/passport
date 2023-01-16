from django.urls import path
from .views import ItemListView, HomeView

urlpatterns = [
   path('items/', ItemListView.as_view(), name='items'),
   path('', HomeView.as_view(), name='home'),
]