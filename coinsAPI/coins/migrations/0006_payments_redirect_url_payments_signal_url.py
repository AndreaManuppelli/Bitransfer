# Generated by Django 4.2.2 on 2023-08-07 13:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("coins", "0005_alter_payments_recived"),
    ]

    operations = [
        migrations.AddField(
            model_name="payments",
            name="redirect_url",
            field=models.CharField(default="https://www.google.it", max_length=1000),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="payments",
            name="signal_url",
            field=models.CharField(default="https://www.google.it", max_length=1000),
            preserve_default=False,
        ),
    ]
