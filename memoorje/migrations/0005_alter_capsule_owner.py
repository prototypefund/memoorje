# Generated by Django 3.2.7 on 2021-09-15 08:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('memoorje', '0004_capsule_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='capsule',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='memoorje.user'),
        ),
    ]