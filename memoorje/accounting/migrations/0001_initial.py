# Generated by Django 3.2.9 on 2022-01-19 09:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('memoorje', '0031_auto_20220117_1146'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('booked_at', models.DateTimeField(null=True)),
                ('is_internal', models.BooleanField()),
                ('external_name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('account_holder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('capsule', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='memoorje.capsule')),
            ],
        ),
    ]