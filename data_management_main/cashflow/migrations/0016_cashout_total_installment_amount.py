# Generated by Django 5.0.5 on 2024-05-14 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cashflow', '0015_alter_cashout_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='cashout',
            name='total_installment_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]