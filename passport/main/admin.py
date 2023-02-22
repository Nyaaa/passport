from django.contrib import admin
from .models import Item, Series, Distributor, Recipient, City, Set, Order
from django.db.models import OuterRef, Subquery


# Register your models here.
class SetItemAdmin(admin.TabularInline):
    model = Set.items.through
    autocomplete_fields = ['item']


class SetAdmin(admin.ModelAdmin):
    list_display = ('serial', 'article', 'comment', 'recipient', 'distributor', 'city', 'date', 'document')
    autocomplete_fields = ['article']
    search_fields = ['serial']
    inlines = (SetItemAdmin,)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('article')
        latest_order = Order.objects.filter(sets=OuterRef('pk')).order_by('-date')[:1]
        qs = qs.prefetch_related('order_set').annotate(recipient=Subquery(latest_order.values('recipient__name')),
                                                       distributor=Subquery(latest_order.values('distributor__name')),
                                                       city=Subquery(latest_order.values('city__name')),
                                                       date=Subquery(latest_order.values('date')),
                                                       document=Subquery(latest_order.values('document')))
        return qs

    def recipient(self, obj):
        return obj.recipient

    def distributor(self, obj):
        return obj.distributor

    def city(self, obj):
        return obj.city

    def date(self, obj):
        return obj.date

    def document(self, obj):
        return obj.document


class ItemAdmin(admin.ModelAdmin):
    list_display = ('article', 'name', 'series', 'is_set')
    list_filter = ('series', 'is_set')
    search_fields = ['article']


class OrderSetAdmin(admin.TabularInline):
    model = Order.sets.through
    autocomplete_fields = ['set']


class OrderAdmin(admin.ModelAdmin):
    list_display = ('date', 'distributor', 'recipient', 'document', 'city', 'comment')
    inlines = (OrderSetAdmin,)


admin.site.register(Item, ItemAdmin)
admin.site.register(Series)
admin.site.register(Distributor)
admin.site.register(Recipient)
admin.site.register(City)
admin.site.register(Set, SetAdmin)
admin.site.register(Order, OrderAdmin)
