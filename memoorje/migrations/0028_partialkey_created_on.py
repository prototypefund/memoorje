# Generated by Django 3.2.9 on 2022-01-05 09:26

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('memoorje', '0027_capsulereceiver_created_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='partialkey',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]