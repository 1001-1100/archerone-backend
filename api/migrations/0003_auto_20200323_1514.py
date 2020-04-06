# Generated by Django 3.0.4 on 2020-03-23 15:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20200323_1435'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='college',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='api.College'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='degree',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='api.Degree'),
            preserve_default=False,
        ),
    ]
