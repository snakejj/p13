# Generated by Django 3.1.7 on 2021-05-02 03:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0006_auto_20210502_0340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='average_interest_rating',
            field=models.DecimalField(decimal_places=2, max_digits=3, null=True),
        ),
        migrations.AlterField(
            model_name='video',
            name='average_quality_rating',
            field=models.DecimalField(decimal_places=2, max_digits=3, null=True),
        ),
    ]
