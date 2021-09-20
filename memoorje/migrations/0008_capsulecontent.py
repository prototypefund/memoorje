# Generated by Django 3.2.7 on 2021-09-20 08:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('memoorje', '0007_auto_20210920_0750'),
    ]

    operations = [
        migrations.CreateModel(
            name='CapsuleContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('capsule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='memoorje.capsule')),
            ],
        ),
    ]
