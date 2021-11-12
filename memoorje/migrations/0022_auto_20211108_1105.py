# Generated by Django 3.2.8 on 2021-11-08 11:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('memoorje', '0021_trustee'),
    ]

    operations = [
        migrations.AddField(
            model_name='trustee',
            name='name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='trustee',
            name='partial_key_hash',
            field=models.CharField(default='', max_length=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='trustee',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AlterUniqueTogether(
            name='trustee',
            unique_together={('capsule', 'partial_key_hash')},
        ),
        migrations.CreateModel(
            name='PartialKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.BinaryField()),
                ('capsule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='memoorje.capsule')),
            ],
        ),
    ]