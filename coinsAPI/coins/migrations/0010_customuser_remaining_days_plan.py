# Generated by Django 4.2.2 on 2023-08-08 12:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("coins", "0009_purchasedplans_username"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="remaining_days_plan",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
