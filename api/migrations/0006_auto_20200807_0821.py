# Generated by Django 3.0.5 on 2020-08-07 08:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20200807_0819'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='building',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.Building'),
        ),
    ]
