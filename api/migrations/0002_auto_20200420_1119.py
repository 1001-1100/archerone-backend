# Generated by Django 3.0.5 on 2020-04-20 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='co_requisite',
            field=models.ManyToManyField(blank=True, related_name='_course_co_requisite_+', to='api.Course'),
        ),
        migrations.AddField(
            model_name='course',
            name='soft_prerequisite_to',
            field=models.ManyToManyField(blank=True, related_name='softprereq', to='api.Course'),
        ),
        migrations.AlterField(
            model_name='course',
            name='prerequisite_to',
            field=models.ManyToManyField(blank=True, related_name='prerequisite', to='api.Course'),
        ),
    ]
