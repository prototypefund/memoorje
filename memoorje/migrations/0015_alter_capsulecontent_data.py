# Generated by Django 3.2.7 on 2021-09-29 15:36

from django.db import migrations

import memoorje.data_storage.fields
import memoorje.data_storage.storage


class Migration(migrations.Migration):

    dependencies = [
        ("memoorje", "0014_user_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="capsulecontent",
            name="data",
            field=memoorje.data_storage.fields.CapsuleDataField(
                storage=memoorje.data_storage.storage.CapsuleDataStorage(location="media/data/"), upload_to=""
            ),
        ),
    ]