# Generated by Django 5.0.2 on 2025-02-16 15:58

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0011_remove_booking_activation_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='activation_code',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
