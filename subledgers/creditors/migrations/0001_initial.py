# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-11-03 06:13
from __future__ import unicode_literals

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bank_reconciliations', '0001_initial'),
        ('ledgers', '0001_initial'),
        ('entities', '0002_entity_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Creditor',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('terms', models.IntegerField(default=14)),
            ],
            options={
                'ordering': ['entity__name'],
            },
        ),
        migrations.CreateModel(
            name='CreditorAccount',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.CharField(default=0, max_length=16)),
                ('account', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='ledgers.Account')),
                ('creditor', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='creditors.Creditor')),
            ],
        ),
        migrations.CreateModel(
            name='CreditorInvoice',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('additional', models.CharField(blank=True,
                                                default='', max_length=128, null=True)),
                ('due_date', models.DateField(null=True)),
                ('invoice_number', models.CharField(max_length=128)),
                ('order_number', models.CharField(
                    blank=True, default='', max_length=128, null=True)),
                ('reference', models.CharField(blank=True,
                                               default='', max_length=128, null=True)),
                ('gst_total', models.DecimalField(
                    decimal_places=2, default=Decimal('0.00'), max_digits=19)),
                ('unpaid', models.DecimalField(decimal_places=2,
                                               default=Decimal('0.00'), max_digits=19)),
                ('is_credit', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('relation', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='creditors.Creditor')),
                ('transaction', models.OneToOneField(blank=True, default='', null=True,
                                                     on_delete=django.db.models.deletion.CASCADE, to='ledgers.Transaction')),
            ],
            options={
                'ordering': ['transaction__date'],
            },
        ),
        migrations.CreateModel(
            name='CreditorLearning',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=64, unique=True)),
                ('creditor', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='creditors.Creditor')),
            ],
        ),
        migrations.CreateModel(
            name='CreditorMatch',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=512)),
                ('bank_entry', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='bank_reconciliations.BankEntry')),
                ('creditor', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='creditors.Creditor')),
            ],
        ),
        migrations.CreateModel(
            name='CreditorPayment',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.CharField(blank=True,
                                          default='', max_length=2048, null=True)),
                ('reference', models.CharField(blank=True,
                                               default='', max_length=128, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('bank_entry', models.OneToOneField(blank=True, default='', null=True,
                                                    on_delete=django.db.models.deletion.CASCADE, to='bank_reconciliations.BankEntry')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CreditorPaymentInvoice',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(decimal_places=2, max_digits=19)),
                ('invoice', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='creditors.CreditorInvoice')),
                ('payment', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='creditors.CreditorPayment')),
            ],
        ),
        migrations.AddField(
            model_name='creditorpayment',
            name='invoices',
            field=models.ManyToManyField(
                blank=True, through='creditors.CreditorPaymentInvoice', to='creditors.CreditorInvoice'),
        ),
        migrations.AddField(
            model_name='creditorpayment',
            name='relation',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to='creditors.Creditor'),
        ),
        migrations.AddField(
            model_name='creditorpayment',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='creditor',
            name='accounts',
            field=models.ManyToManyField(
                blank=True, through='creditors.CreditorAccount', to='ledgers.Account'),
        ),
        migrations.AddField(
            model_name='creditor',
            name='default_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='creditor_default', to='ledgers.Account'),
        ),
        migrations.AddField(
            model_name='creditor',
            name='entity',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, related_name='creditors', to='entities.Entity'),
        ),
        migrations.AlterUniqueTogether(
            name='creditorinvoice',
            unique_together=set([('invoice_number', 'relation')]),
        ),
    ]
