# Generated by Django 5.0.7 on 2025-02-02 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='amount',
            field=models.PositiveIntegerField(),
        ),
    ]
