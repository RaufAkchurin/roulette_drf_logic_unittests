# Generated by Django 4.1.7 on 2023-09-15 11:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roulette_app', '0008_alter_spinround_last_step'),
    ]

    operations = [
        migrations.AddField(
            model_name='spinround',
            name='created_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='spinround',
            name='last_step',
            field=models.IntegerField(default=1, validators=[django.core.validators.MaxValueValidator(limit_value=11, message='last_step не должен быть больше 11.'), django.core.validators.MinValueValidator(limit_value=1, message='last_step не должен быть меньше 0.')]),
        ),
    ]
