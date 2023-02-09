from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import CommonDelete, CommonListView, CreateUpdateView
from .models import Item, Series, Distributor, Recipient, Set, Order, City
from . import views as v

urlpatterns = [
    path('', v.HomeView.as_view(), name='home'),
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('item/', v.ItemListView.as_view(), name='item'),
    path('item/create/', CreateUpdateView.as_view(model=Item), name='item_create'),
    path('item/<str:pk>/', CreateUpdateView.as_view(model=Item), name='item_edit'),
    path('item/<str:pk>/delete/', CommonDelete.as_view(model=Item), name='item_delete'),
    path('set/', v.SetListView.as_view(), name='set'),
    path('set/create/', CreateUpdateView.as_view(model=Set), name='set_create'),
    path('set/<str:pk>/', v.SetDetailView.as_view(), name='set_detail'),
    path('set/<str:pk>/edit/', v.SetUpdateView.as_view(), name='set_edit'),
    path('set/<str:pk>/delete/', CommonDelete.as_view(model=Set), name='set_delete'),
    path('order/', v.OrderListView.as_view(), name='order'),
    path('order/create/', CreateUpdateView.as_view(model=Order), name='order_create'),
    path('order/<int:pk>/', v.OrderDetailView.as_view(), name='order_detail'),
    path('order/<int:pk>/edit/', v.OrderUpdateView.as_view(), name='order_edit'),
    path('order/<int:pk>/delete/', CommonDelete.as_view(model=Order), name='order_delete'),
]

generic_views = [Series, City, Distributor, Recipient]
for model in generic_views:
    text = model.__name__.lower()
    urlpatterns += [
        path(f'{text}/', CommonListView.as_view(model=model), name=f'{text}'),
        path(f'{text}/create/', CreateUpdateView.as_view(model=model), name=f'{text}_create'),
        path(f'{text}/<int:pk>/', CreateUpdateView.as_view(model=model), name=f'{text}_edit'),
        path(f'{text}/<int:pk>/delete/', CommonDelete.as_view(model=model), name=f'{text}_delete'),
    ]
