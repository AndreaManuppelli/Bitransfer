# Generated by Django 4.2.2 on 2023-08-08 12:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("coins", "0007_alter_payments_redirect_url_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="PurchasedPlans",
            fields=[
                ("id", models.UUIDField(primary_key=True, serialize=False)),
                ("address", models.CharField(max_length=150)),
                ("creation", models.DateTimeField()),
                ("amount", models.FloatField()),
                ("paid", models.BooleanField()),
                ("plan_id", models.IntegerField()),
                ("withdrawn", models.BooleanField()),
                ("incorrect_payment", models.BooleanField()),
                ("recived", models.FloatField()),
                ("datetime_payment_confirmed", models.DateTimeField(null=True)),
            ],
        ),
    ]