# Generated by Django 5.0.6 on 2024-05-30 15:10

import django.db.models.deletion

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("wagtail_newsletter", "0001_initial"),
        ("wagtailcore", "0093_uploadedfile"),
    ]

    operations = [
        migrations.CreateModel(
            name="PageLockedForNewsletter",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "page",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="wagtailcore.page",
                    ),
                ),
            ],
        ),
    ]
