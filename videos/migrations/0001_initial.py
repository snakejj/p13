# Generated by Django 3.1.7 on 2021-04-07 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.CharField(max_length=11)),
                ('added_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('IN', 'initial'), ('RE', 'reported'), ('ON', 'on'), ('OF', 'off')], default='IN', max_length=2)),
            ],
        ),
    ]
