# Generated by Django 3.2.7 on 2021-09-15 07:30

from django.db import migrations, models
import memoorje.models


class Migration(migrations.Migration):

    dependencies = [
        ('memoorje', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', memoorje.models.UserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='email address'),
        ),
    ]
