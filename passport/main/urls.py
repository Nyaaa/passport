from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views as v
from .models import City, Distributor, Item, Order, Recipient, Series, Set
from .views import CommonDeleteView, CommonListView, CommonUpdateView

urlpatterns = [
    path('', v.HomeView.as_view(), name='home'),
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('item/', v.ItemListView.as_view(), name='item'),
    path('incomplete/', v.IncompleteSetView.as_view(), name='incomplete'),
    path('item/<str:pk>/edit/', CommonUpdateView.as_view(model=Item), name='item_edit'),
    path('item/<str:pk>/delete/', CommonDeleteView.as_view(model=Item), name='item_delete'),
    path('set/', v.SetListView.as_view(), name='set'),
    path('set/<str:pk>/', v.SetDetailView.as_view(), name='set_detail'),
    path('set/<str:pk>/edit/', v.SetUpdateView.as_view(), name='set_edit'),
    path('set/<str:pk>/delete/', CommonDeleteView.as_view(model=Set), name='set_delete'),
    path('order/', v.OrderListView.as_view(), name='order'),
    path('order/create/', v.OrderCreateView.as_view(), name='order_create'),
    path('order/<int:pk>/', v.OrderDetailView.as_view(), name='order_detail'),
    path('order/<int:pk>/edit/', v.OrderUpdateView.as_view(), name='order_edit'),
    path('order/<int:pk>/delete/', CommonDeleteView.as_view(model=Order), name='order_delete'),
]

generic_views = [Series, City, Distributor, Recipient]
for model in generic_views:
    text = model.__name__.lower()
    urlpatterns += [
        path(f'{text}/', CommonListView.as_view(model=model), name=f'{text}'),
        path(f'{text}/<int:pk>/edit/', CommonUpdateView.as_view(model=model), name=f'{text}_edit'),
        path(f'{text}/<int:pk>/delete/', CommonDeleteView.as_view(model=model), name=f'{text}_delete'),
    ]
