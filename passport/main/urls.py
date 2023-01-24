from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import ItemListView, HomeView, CommonUpdate, CommonListCreate, \
   CommonDelete, SetListView, SetUpdateView, ItemAutocomplete
from .models import Item, Series, Distributor, Recipient, Set

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
   path('distributor/', CommonListCreate.as_view(model=Distributor), name='distributor'),
   path('distributor/<int:pk>', CommonUpdate.as_view(model=Distributor), name='distributor_edit'),
   path('distributor/<int:pk>/delete', CommonDelete.as_view(model=Distributor), name='distributor_delete'),
   path('recipient/', CommonListCreate.as_view(model=Recipient), name='recipient'),
   path('recipient/<int:pk>', CommonUpdate.as_view(model=Recipient), name='recipient_edit'),
   path('recipient/<int:pk>/delete', CommonDelete.as_view(model=Recipient), name='recipient_delete'),
   path('set/', SetListView.as_view(), name='set'),
   path('set/<str:pk>', SetUpdateView.as_view(), name='set_edit'),
   path('set/<str:pk>/delete', CommonDelete.as_view(model=Set), name='set_delete'),
   path('item-autocomplete/', ItemAutocomplete.as_view(), name='item-autocomplete'),
]
