# Generated by Django 4.1.7 on 2023-09-18 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roulette_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='spin',
            name='created_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
