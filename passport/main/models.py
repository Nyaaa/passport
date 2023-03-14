from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.db.models import ProtectedError
from django.core.validators import MinValueValidator
import uuid
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy


# Create your models here.
class Series(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_('Name'))

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = pgettext_lazy('singular', 'Series')
        verbose_name_plural = pgettext_lazy('plural', 'Series')


def item_img_path(instance, filename):
    ext = filename.split('.')[-1].lower()
    if instance:
        filename = f'item_img/{instance.pk}.{ext}'
    else:
        # adding just in case, this should never trigger
        filename = f'item_img/{uuid.uuid4()}.{ext}'
    return filename


class Item(models.Model):
    article = models.CharField(max_length=50, primary_key=True, verbose_name=_('Article'))
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    series = models.ForeignKey(Series, on_delete=models.RESTRICT, blank=True, null=True, default=None,
                               verbose_name=pgettext_lazy('singular', 'Series'))
    is_set = models.BooleanField(default=False, verbose_name=_('Is set'))
    image = models.ImageField(upload_to=item_img_path, blank=True, null=True, verbose_name=_('Image'))

    def __str__(self):
        return f'{self.article}'

    class Meta:
        verbose_name = _('Item')
        verbose_name_plural = _('Items')

    def get_absolute_url(self):
        return reverse('item_edit', args=[self.pk])


class SetItem(models.Model):
    set = models.ForeignKey('Set', on_delete=models.CASCADE, verbose_name=_('Set'))
    item = models.ForeignKey(Item, on_delete=models.RESTRICT, verbose_name=_('Item'))
    amount = models.IntegerField(default=1,
                                 validators=[MinValueValidator(0, _('Quantity should be >= 0.'))],
                                 verbose_name=_('Amount'))
    tray = models.IntegerField(default=1, help_text=_('Select tray 0 for optional items.'),
                               verbose_name=_('Tray'))
    comment = models.TextField(blank=True, null=True, verbose_name=_('Comment'))


class Set(models.Model):
    serial = models.CharField(max_length=50, primary_key=True, verbose_name=_('Serial'))
    article = models.ForeignKey(Item, related_name='set_article', on_delete=models.RESTRICT,
                                verbose_name=_('Article'))
    items = models.ManyToManyField(Item, through=SetItem, verbose_name=_('Items'))
    comment = models.TextField(blank=True, null=True, verbose_name=_('Comment'))

    def __str__(self):
        return f'{self.serial}'

    class Meta:
        verbose_name = _('Set')
        verbose_name_plural = _('Sets')

    def get_absolute_url(self):
        return reverse('set_detail', args=[self.pk])


class Distributor(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Name'))

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = _('Distributor')
        verbose_name_plural = _('Distributors')

    def delete(self, *args, **kwargs):
        if self.pk == 1:
            raise ProtectedError(_('This is a system object.'), self)
        else:
            super(Distributor, self).delete(*args, **kwargs)


class Recipient(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Name'))

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = _('Recipient')
        verbose_name_plural = _('Recipients')

    def delete(self, *args, **kwargs):
        if self.pk in (1, 2):
            raise ProtectedError(_('This is a system object.'), self)
        else:
            super(Recipient, self).delete(*args, **kwargs)


class City(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Name'))

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = _("City")
        verbose_name_plural = _("Cities")


class OrderSet(models.Model):
    set = models.ForeignKey(Set, on_delete=models.RESTRICT)
    order = models.ForeignKey('Order', on_delete=models.CASCADE)


class Order(models.Model):
    date = models.DateTimeField(default=timezone.now, verbose_name=_('Date'))
    distributor = models.ForeignKey(Distributor, on_delete=models.RESTRICT, verbose_name=_('Distributor'))
    recipient = models.ForeignKey(Recipient, on_delete=models.RESTRICT, verbose_name=_('Recipient'))
    document = models.IntegerField(blank=True, null=True, unique=True, verbose_name=_('Document'))
    city = models.ForeignKey(City, on_delete=models.RESTRICT, verbose_name=_('City'))
    sets = models.ManyToManyField(Set, through=OrderSet, verbose_name=_('Sets'))
    comment = models.TextField(blank=True, null=True, verbose_name=_('Comment'))

    def __str__(self):
        return f'{self.pk}'

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    def get_absolute_url(self):
        return reverse('order_detail', args=[self.pk])
