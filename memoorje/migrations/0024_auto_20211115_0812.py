# Generated by Django 3.2.9 on 2021-11-15 08:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('memoorje', '0023_alter_trustee_partial_key_hash'),
    ]

    operations = [
        migrations.AddField(
            model_name='capsule',
            name='capsule',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='memoorje.capsule'),
        ),
        migrations.AlterField(
            model_name='capsulereceiver',
            name='capsule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receivers', to='memoorje.capsule'),
        ),
    ]
