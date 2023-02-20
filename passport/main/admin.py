from django.contrib import admin
from .models import Item, Series, Distributor, Recipient, City, Set, Order


# Register your models here.
class SetAdmin(admin.ModelAdmin):
    list_display = ('serial', 'article', 'comment')
    list_filter = ('article',)


admin.site.register(Item)
admin.site.register(Series)
admin.site.register(Distributor)
admin.site.register(Recipient)
admin.site.register(City)
admin.site.register(Set, SetAdmin)
admin.site.register(Order)
