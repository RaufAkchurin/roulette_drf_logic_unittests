# Generated by Django 4.1.7 on 2023-09-19 06:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('roulette_app', '0002_spin_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spin',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='spin_users', to=settings.AUTH_USER_MODEL),
        ),
    ]