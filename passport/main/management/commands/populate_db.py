import random
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.db.models import Max, Count
from main.models import Item, Distributor, Recipient, Order, City, Set, Series, SetItem
from faker import Faker

fake = Faker()


class Command(BaseCommand):
    help = 'Populates the database with random generated data.'

    def add_arguments(self, parser):
        parser.add_argument('--items', type=int, help='The amount of item articles to create.')
        parser.add_argument('--orders', type=int, help='The amount of orders to create.')

    def handle(self, *args, **options):
        for _ in range(20):
            City.objects.get_or_create(name=fake.city())
            Distributor.objects.get_or_create(name=fake.company())
            Recipient.objects.get_or_create(name=fake.company())
            Series.objects.get_or_create(name=fake.safe_color_name())

        items = options['items'] if options['items'] else 1500
        orders = options['orders'] if options['orders'] else 2000

        for _ in range(50):
            self.gen_items(True)
        for _ in range(items - 50):
            self.gen_items(False)

        for i in Item.objects.filter(is_set=True):
            for j in range(50):
                Set.objects.get_or_create(serial=f'{i}-{j:04}', article=i)

        for _ in range(orders):
            Order.objects.get_or_create(date=fake.date_time_this_decade(tzinfo=timezone.utc),
                                        distributor=random.choice(Distributor.objects.all()),
                                        recipient=random.choice(Recipient.objects.all()),
                                        document=fake.unique.random_int(min=1, max=999999),
                                        city=random.choice(City.objects.all())
                                        )

        st = list(Set.objects.all())
        itm = list(Item.objects.all())

        for i in Set.objects.all():
            i.items.add(*random.sample(itm, 10))

        for i in Order.objects.all():
            i.sets.add(*random.sample(st, 4))

        self.stdout.write(self.style.SUCCESS('Successfully populated the database.'))

    def gen_items(self, is_set: bool):
        Item.objects.get_or_create(name=fake.text(max_nb_chars=20),
                                   article=fake.bothify(text='??###?', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
                                   series=random.choice(Series.objects.all()),
                                   is_set=is_set)
