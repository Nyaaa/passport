import random

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from main.models import City, Distributor, Item, Order, Recipient, Series, Set, SetItem

fake = Faker()


class Command(BaseCommand):
    help = 'Populates the database with random generated data.'  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument('--items', type=int, help='The amount of item articles to create.')
        parser.add_argument('--orders', type=int, help='The amount of orders to create.')

    def handle(self, *args, **options):
        items = options['items'] if options['items'] else 1500
        orders = options['orders'] if options['orders'] else 2000
        lst = []

        City.objects.bulk_create([City(name=fake.city()) for _ in range(20)], ignore_conflicts=True)
        Distributor.objects.bulk_create([Distributor(name=fake.company()) for _ in range(20)], ignore_conflicts=True)
        Recipient.objects.bulk_create([Recipient(name=fake.company()) for _ in range(20)], ignore_conflicts=True)
        Series.objects.bulk_create([Series(name=fake.safe_color_name()) for _ in range(20)], ignore_conflicts=True)
        Item.objects.bulk_create(self.gen_items(items, is_set=True), ignore_conflicts=True)
        Item.objects.bulk_create(self.gen_items(items, is_set=False), ignore_conflicts=True)
        Order.objects.bulk_create(self.gen_orders(orders))

        for i in Item.objects.filter(is_set=True):
            lst += [Set(serial=f'{i}-{j:04}', article=i) for j in range(50)]
        Set.objects.bulk_create(lst)
        lst.clear()

        st = list(Set.objects.all())
        itm = list(Item.objects.all())

        for i in st:
            items = random.sample(itm, 10)
            lst += [SetItem(set=i, item=j) for j in items]
        SetItem.objects.bulk_create(lst)
        lst.clear()

        for i in Order.objects.all():
            sets = random.sample(st, 4)
            lst += [Order.sets.through(order=i, set=j) for j in sets]
        Order.sets.through.objects.bulk_create(lst)

        self.stdout.write(self.style.SUCCESS('Successfully populated the database.'))

    @staticmethod
    def gen_items(items, is_set: bool) -> list[Item]:
        amount = 50 if is_set else items - 50
        return [Item(name=fake.text(max_nb_chars=20),
                     article=fake.bothify(text='??###?', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
                     series=random.choice(Series.objects.all()),
                     is_set=is_set)
                for _ in range(amount)]

    @staticmethod
    def gen_orders(orders) -> list[Order]:
        recip = Recipient.objects.filter(pk__in=(1, 2)).order_by('-pk')
        bulk_list = []
        for _ in range(orders):
            distributor = random.choice(Distributor.objects.all())
            if distributor.pk == 1:
                recipient = random.choices(recip, weights=(20, 10))[0]
            else:
                recipient = random.choice(Recipient.objects.exclude(pk__in=(1, 2)))

            bulk_list.append(Order(date=fake.date_time_this_decade(tzinfo=timezone.utc),
                                   distributor=distributor,
                                   recipient=recipient,
                                   document=fake.unique.random_int(min=100000, max=999999),
                                   city=random.choice(City.objects.all())
                                   ))
        return bulk_list
