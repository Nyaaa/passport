from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.db.models import ProtectedError
from django.core.validators import MinValueValidator
import uuid
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext


# Create your models here.
class Series(models.Model):
    name = models.CharField(_('Name'), max_length=50, unique=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = pgettext('singular', 'Series')
        verbose_name_plural = pgettext('plural', 'Series')


def item_img_path(instance, filename):
    ext = filename.split('.')[-1].lower()
    if instance:
        filename = f'item_img/{instance.pk}.{ext}'
    else:
        # adding just in case, this should never trigger
        filename = f'item_img/{uuid.uuid4()}.{ext}'
    return filename


class Item(models.Model):
    article = models.CharField(_('Article'), max_length=50, primary_key=True)
    name = models.CharField(_('Name'), max_length=255)
    series = models.ForeignKey(Series, on_delete=models.RESTRICT, blank=True, null=True, default=None)
    is_set = models.BooleanField(_('Is set'), default=False)
    image = models.ImageField(_('Image'), upload_to=item_img_path, blank=True, null=True)

    def __str__(self):
        return f'{self.article}'

    class Meta:
        verbose_name = _('Item')
        verbose_name_plural = _('Items')

    def get_absolute_url(self):
        return reverse('item_edit', args=[self.pk])


class SetItem(models.Model):
    set = models.ForeignKey('Set', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.RESTRICT)
    amount = models.IntegerField(_('Amount'), default=1,
                                 validators=[MinValueValidator(0, _('Quantity should be >= 0.'))])
    tray = models.IntegerField(_('Tray'), default=1, help_text=_('Select tray 0 for optional items.'))
    comment = models.TextField(_('Comment'), blank=True, null=True)


class Set(models.Model):
    serial = models.CharField(_('Serial'), max_length=50, primary_key=True)
    article = models.ForeignKey(Item, related_name='set_article', on_delete=models.RESTRICT)
    items = models.ManyToManyField(Item, through=SetItem)
    comment = models.TextField(_('Comment'), blank=True, null=True)

    def __str__(self):
        return f'{self.serial}'

    class Meta:
        verbose_name = _('Set')
        verbose_name_plural = _('Sets')

    def get_absolute_url(self):
        return reverse('set_detail', args=[self.pk])


class Distributor(models.Model):
    name = models.CharField(_('Name'), max_length=255, unique=True)

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
    name = models.CharField(_('Name'), max_length=255, unique=True)

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
    name = models.CharField(_('Name'), max_length=255, unique=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = _("City")
        verbose_name_plural = _("Cities")


class OrderSet(models.Model):
    set = models.ForeignKey(Set, on_delete=models.RESTRICT)
    order = models.ForeignKey('Order', on_delete=models.CASCADE)


class Order(models.Model):
    date = models.DateTimeField(_('Date'), default=timezone.now)
    distributor = models.ForeignKey(Distributor, on_delete=models.RESTRICT)
    recipient = models.ForeignKey(Recipient, on_delete=models.RESTRICT)
    document = models.IntegerField(_('Document'), blank=True, null=True, unique=True)
    city = models.ForeignKey(City, on_delete=models.RESTRICT)
    sets = models.ManyToManyField(Set, through=OrderSet)
    comment = models.TextField(_('Comment'), blank=True, null=True)

    def __str__(self):
        return f'{self.pk}'

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    def get_absolute_url(self):
        return reverse('order_detail', args=[self.pk])
