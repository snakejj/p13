# Generated by Django 3.1.7 on 2021-05-02 03:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0005_auto_20210502_0321'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ratevideo',
            name='average_interest_rating',
        ),
        migrations.RemoveField(
            model_name='ratevideo',
            name='average_quality_rating',
        ),
        migrations.AddField(
            model_name='video',
            name='average_interest_rating',
            field=models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=3),
        ),
        migrations.AddField(
            model_name='video',
            name='average_quality_rating',
            field=models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=3),
        ),
    ]