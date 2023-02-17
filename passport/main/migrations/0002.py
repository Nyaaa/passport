from django.db import migrations


def preload(apps, schema_editor):
    distributor = apps.get_model('main', 'Distributor')
    distributor.objects.create(name='Warehouse')
    recipient = apps.get_model('main', 'Recipient')
    recipient.objects.create(name='[Incomplete]')
    recipient.objects.create(name='[Main]')

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(preload),
    ]