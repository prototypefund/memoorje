# Generated by Django 3.2.7 on 2021-09-28 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memoorje', '0013_alter_capsule_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='name',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
