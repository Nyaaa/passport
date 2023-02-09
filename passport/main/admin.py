from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Order, Set


# Register your models here.
class OrderResource(resources.ModelResource):

    class Meta:
        model = Order
        fields = ('date', 'distributor__name', 'recipient__name', 'city__name', 'document', 'sets', 'comment')
        export_order = fields


class OrderAdmin(ImportExportModelAdmin):
    resource_classes = [OrderResource]


class SetAdmin(ImportExportModelAdmin):
    pass


admin.site.register(Order, OrderAdmin)
admin.site.register(Set, SetAdmin)
