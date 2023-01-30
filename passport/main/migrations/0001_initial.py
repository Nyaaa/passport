# Generated by Django 4.1.5 on 2023-01-30 09:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Distributor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('article', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('is_set', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Recipient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Series',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Set',
            fields=[
                ('serial', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('comment', models.TextField(blank=True, null=True)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='set_article', to='main.item')),
            ],
        ),
        migrations.CreateModel(
            name='SetItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(default=1)),
                ('tray', models.IntegerField(default=1)),
                ('comment', models.TextField(blank=True, null=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.item')),
                ('set', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.set')),
            ],
        ),
        migrations.AddField(
            model_name='set',
            name='items',
            field=models.ManyToManyField(through='main.SetItem', to='main.item'),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('document', models.IntegerField(blank=True, null=True, unique=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='main.city')),
                ('distributor', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='main.distributor')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='main.recipient')),
                ('sets', models.ManyToManyField(to='main.set')),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='series',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.RESTRICT, to='main.series'),
        ),
    ]
