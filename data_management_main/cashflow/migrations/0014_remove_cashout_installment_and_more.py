# Generated by Django 5.0.5 on 2024-05-14 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cashflow', '0013_cashout'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cashout',
            name='installment',
        ),
        migrations.RemoveField(
            model_name='cashout',
            name='installment_amount',
        ),
        migrations.RemoveField(
            model_name='cashout',
            name='installment_date',
        ),
        migrations.AddField(
            model_name='cashout',
            name='installments',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cashout',
            name='cost_center',
            field=models.CharField(blank=True, choices=[('catalyst', 'Catalyst'), ('other', 'Other')], default='catalyst', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='cashout',
            name='service_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='cashout',
            name='status',
            field=models.CharField(choices=[('Received', 'Received'), ('Pending', 'Pending'), ('Processed', 'Processed')], default='Received', max_length=50),
        ),
    ]
