# Generated by Django 5.2 on 2025-04-08 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advanced_learning', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userproject',
            name='notes',
            field=models.TextField(blank=True, help_text='Ghi chú của người dùng về dự án', null=True),
        ),
    ]
