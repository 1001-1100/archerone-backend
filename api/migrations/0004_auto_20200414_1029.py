# Generated by Django 3.0.5 on 2020-04-14 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20200413_1837'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
