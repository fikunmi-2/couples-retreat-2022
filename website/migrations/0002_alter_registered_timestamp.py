# Generated by Django 4.1 on 2022-08-05 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="registered",
            name="timestamp",
            field=models.CharField(max_length=120, verbose_name="Timestamp"),
        ),
    ]
