# Generated by Django 3.2.9 on 2022-02-18 09:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('memoorje', '0033_keyslot_recipient'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='partialkey',
            unique_together={('capsule', 'data')},
        ),
    ]