# Generated by Django 3.2.8 on 2021-11-08 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memoorje', '0022_auto_20211108_1105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trustee',
            name='partial_key_hash',
            field=models.BinaryField(),
        ),
    ]