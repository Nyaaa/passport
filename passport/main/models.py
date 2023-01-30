from django.db import models
from django.utils.functional import cached_property


# Create your models here.
class Series(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f'{self.name}'


class Item(models.Model):
    article = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    series = models.ForeignKey(Series, on_delete=models.RESTRICT, blank=True, null=True, default=None)
    is_set = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.article}'


class SetItem(models.Model):
    set = models.ForeignKey('Set', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    amount = models.IntegerField(default=1)
    tray = models.IntegerField(default=1)
    comment = models.TextField(blank=True, null=True)


class Set(models.Model):
    serial = models.CharField(max_length=50, primary_key=True)
    article = models.ForeignKey(Item, related_name='set_article', on_delete=models.RESTRICT)
    items = models.ManyToManyField(Item, through=SetItem)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.serial}'

    @cached_property
    def assigned_to(self):
        return self.order_set.select_related().filter(sets=self).order_by('date').last()



class Distributor(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f'{self.name}'


class Recipient(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f'{self.name}'


class City(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f'{self.name}'


class Order(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    distributor = models.ForeignKey(Distributor, on_delete=models.RESTRICT)
    recipient = models.ForeignKey(Recipient, on_delete=models.RESTRICT)
    document = models.IntegerField(blank=True, null=True, unique=True)
    city = models.ForeignKey(City, on_delete=models.RESTRICT)
    sets = models.ManyToManyField(Set)
    comment = models.TextField(blank=True, null=True)
