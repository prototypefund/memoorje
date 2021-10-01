# Generated by Django 3.2.7 on 2021-10-01 09:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('memoorje', '0015_alter_capsulecontent_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='CapsuleReceiver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('capsule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='memoorje.capsule')),
            ],
            options={
                'unique_together': {('capsule', 'email')},
            },
        ),
    ]
