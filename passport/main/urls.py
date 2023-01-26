from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import ItemListView, HomeView, CommonUpdate, CommonListCreate, \
   CommonDelete, SetListView, ItemAutocomplete, set_items, SetDetailView, OrderListView, \
   CityAutocomplete, SetAutocomplete, OrderDetailView
from .models import Item, Series, Distributor, Recipient, Set, Order, City

urlpatterns = [
   path('', HomeView.as_view(), name='home'),
   path('login/', LoginView.as_view(template_name='login.html'), name='login'),
   path('logout/', LogoutView.as_view(template_name='logout.html'), name='logout'),
   path('item/', ItemListView.as_view(), name='item'),
   path('item/<str:pk>', CommonUpdate.as_view(model=Item), name='item_edit'),
   path('item/<str:pk>/delete', CommonDelete.as_view(model=Item), name='item_delete'),
   path('series/', CommonListCreate.as_view(model=Series), name='series'),
   path('series/<int:pk>', CommonUpdate.as_view(model=Series), name='series_edit'),
   path('series/<int:pk>/delete', CommonDelete.as_view(model=Series), name='series_delete'),
   path('city/', CommonListCreate.as_view(model=City), name='city'),
   path('city/<int:pk>', CommonUpdate.as_view(model=City), name='city_edit'),
   path('city/<int:pk>/delete', CommonDelete.as_view(model=City), name='city_delete'),
   path('distributor/', CommonListCreate.as_view(model=Distributor), name='distributor'),
   path('distributor/<int:pk>', CommonUpdate.as_view(model=Distributor), name='distributor_edit'),
   path('distributor/<int:pk>/delete', CommonDelete.as_view(model=Distributor), name='distributor_delete'),
   path('recipient/', CommonListCreate.as_view(model=Recipient), name='recipient'),
   path('recipient/<int:pk>', CommonUpdate.as_view(model=Recipient), name='recipient_edit'),
   path('recipient/<int:pk>/delete', CommonDelete.as_view(model=Recipient), name='recipient_delete'),
   path('set/', SetListView.as_view(), name='set'),
   path('set/<str:pk>/edit', set_items, name='set_edit'),
   path('set/<str:pk>', SetDetailView.as_view(), name='set_detail'),
   path('set/<str:pk>/delete', CommonDelete.as_view(model=Set), name='set_delete'),
   path('item-autocomplete/', ItemAutocomplete.as_view(), name='item-autocomplete'),
   path('city-autocomplete/', CityAutocomplete.as_view(), name='city-autocomplete'),
   path('set-autocomplete/', SetAutocomplete.as_view(), name='set-autocomplete'),
   path('order/', OrderListView.as_view(), name='order_list'),
   path('order/<int:pk>', OrderDetailView.as_view(), name='order_detail'),
   path('order/<int:pk>/edit', CommonUpdate.as_view(model=Order), name='order_edit'),
   path('order/<int:pk>/delete', CommonDelete.as_view(model=Order), name='order_delete'),
]
