from django.db import models
from cities_light.models import City


# Create your models here.
class Item(models.Model):
    article = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)


class SetItem(models.Model):
    set = models.ForeignKey('Set', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    amount = models.IntegerField(default=1)
    extra = models.BooleanField(default=False)
    accounted = models.BooleanField(default=True)
    comment = models.TextField(blank=True)


class Series(models.Model):
    name = models.CharField(max_length=50)


class Set(models.Model):
    serial = models.CharField(max_length=50, primary_key=True)
    set_article = models.ForeignKey(Item, related_name='%(class)s_article', on_delete=models.RESTRICT)
    items = models.ManyToManyField(Item, through=SetItem)
    accounted = models.BooleanField(default=True)
    series = models.ForeignKey(Series, on_delete=models.RESTRICT)


class Distributor(models.Model):
    name = models.CharField(max_length=255)


class Recipient(models.Model):
    name = models.CharField(max_length=255)


class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    set = models.ForeignKey(Set, on_delete=models.CASCADE)
    amount = models.IntegerField(default=1)


class Order(models.Model):
    date = models.DateTimeField()
    distributor = models.ForeignKey(Distributor, on_delete=models.RESTRICT)
    recipient = models.ForeignKey(Recipient, on_delete=models.RESTRICT)
    document = models.IntegerField()
    city = models.ForeignKey(City, on_delete=models.RESTRICT)
    sets = models.ManyToManyField(Set, through=OrderItem)
