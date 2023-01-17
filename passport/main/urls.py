from django.urls import path
from .views import ItemListView, HomeView, ItemUpdate, ListAndCreate

urlpatterns = [
   path('items/', ItemListView.as_view(), name='items'),
   path('', HomeView.as_view(), name='home'),
   path('items/<str:pk>', ItemUpdate.as_view(), name='item_edit'),
   path('series/', ListAndCreate.as_view(), name='series'),
]