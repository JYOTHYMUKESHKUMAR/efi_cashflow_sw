# Generated by Django 5.0.5 on 2024-05-11 23:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cashflow', '0010_remove_cashin_num_installments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cashin',
            name='admin',
        ),
    ]