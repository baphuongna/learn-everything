# Generated by Django 5.2 on 2025-04-07 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="subject",
            name="icon",
            field=models.ImageField(blank=True, null=True, upload_to="subject_images/"),
        ),
    ]
