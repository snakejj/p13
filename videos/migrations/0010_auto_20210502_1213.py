# Generated by Django 3.1.7 on 2021-05-02 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0009_abusevideo_report_pending'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='abusevideo',
            name='report_pending',
        ),
        migrations.AddField(
            model_name='abusevideo',
            name='report_dealt_with',
            field=models.BooleanField(default=False),
        ),
    ]
