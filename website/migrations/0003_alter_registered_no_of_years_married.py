# Generated by Django 4.1 on 2022-08-05 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0002_alter_registered_timestamp"),
    ]

    operations = [
        migrations.AlterField(
            model_name="registered",
            name="no_of_years_married",
            field=models.CharField(
                max_length=5, verbose_name="Number of Years married"
            ),
        ),
    ]