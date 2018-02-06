# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-29 09:19
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('element', models.CharField(choices=[('01', 'Asset'), ('03', 'Liability'), ('05', "Owner's Equity"), ('10', 'Revenue'), ('15', 'Expenses')], max_length=2)),
                ('number', models.CharField(blank=True, default=None, max_length=4)),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField(blank=True, default='')),
                ('special_account', models.CharField(blank=True, choices=[('ACP', 'Accounts Payable Liability Account'), ('ACR', 'Accounts Receivable Asset Account'), ('bank', 'Bank Account'), ('owner', 'Owner Equity'), ('suspense', 'Holding/Suspense')], default=None, max_length=8, null=True)),
                ('parent', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parent+', to='ledgers.Account')),
            ],
            options={
                'ordering': ['element', 'number', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Line',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(decimal_places=2, max_digits=19)),
                ('note', models.CharField(blank=True, default='', max_length=2048)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='ledgers.Account')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('value', models.DecimalField(decimal_places=2, max_digits=19)),
                ('note', models.CharField(blank=True, default='', max_length=2048, null=True)),
                ('source', models.CharField(max_length=1024)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_balanced', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.AddField(
            model_name='line',
            name='transaction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='ledgers.Transaction'),
        ),
        migrations.AddField(
            model_name='account',
            name='tags',
            field=models.ManyToManyField(blank=True, default=None, related_name='accounts', to='ledgers.Tag'),
        ),
    ]
