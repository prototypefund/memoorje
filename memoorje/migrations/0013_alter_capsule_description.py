# Generated by Django 3.2.7 on 2021-09-27 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memoorje', '0012_alter_capsulecontent_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='capsule',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
