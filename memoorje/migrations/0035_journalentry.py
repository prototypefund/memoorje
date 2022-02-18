# Generated by Django 3.2.9 on 2022-02-18 10:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('memoorje', '0034_alter_partialkey_unique_together'),
    ]

    operations = [
        migrations.CreateModel(
            name='JournalEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('action', models.CharField(choices=[('c', 'Create'), ('u', 'Update'), ('d', 'Delete')], max_length=1)),
                ('entity_id', models.PositiveIntegerField()),
                ('capsule', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='memoorje.capsule')),
                ('entity_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]