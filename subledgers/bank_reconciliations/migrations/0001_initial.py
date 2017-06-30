# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-30 02:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bank_accounts', '0001_initial'),
        ('ledgers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('additional', models.CharField(blank=True, default='', max_length=128, null=True)),
            ],
            options={
                'verbose_name_plural': 'bank entries',
            },
        ),
        migrations.CreateModel(
            name='BankLearning',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=64)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ledgers.Account')),
            ],
        ),
        migrations.CreateModel(
            name='BankTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('value', models.DecimalField(decimal_places=2, max_digits=19)),
                ('line_dump', models.CharField(max_length=2048)),
                ('description', models.CharField(max_length=512)),
                ('additional', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('balance', models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=19, null=True)),
                ('not_now', models.BooleanField(default=False)),
                ('note', models.CharField(blank=True, default=None, max_length=64, null=True)),
                ('bank_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='banktransactions', to='bank_accounts.BankAccount')),
                ('tags', models.ManyToManyField(blank=True, default=None, related_name='banktransactions', to='ledgers.Tag')),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.AddField(
            model_name='bankentry',
            name='bank_transaction',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='bank_reconciliations.BankTransaction'),
        ),
        migrations.AddField(
            model_name='bankentry',
            name='transaction',
            field=models.OneToOneField(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='ledgers.Transaction'),
        ),
    ]
