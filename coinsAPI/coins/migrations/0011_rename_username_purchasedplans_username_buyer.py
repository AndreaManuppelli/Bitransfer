# Generated by Django 4.2.2 on 2023-08-08 13:13

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("coins", "0010_customuser_remaining_days_plan"),
    ]

    operations = [
        migrations.RenameField(
            model_name="purchasedplans",
            old_name="username",
            new_name="username_buyer",
        ),
    ]
