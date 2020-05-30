# Generated by Django 2.2.12 on 2020-05-30 01:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oficios', '0003_auto_20200529_2100'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicaloficio',
            name='categories',
        ),
        migrations.RemoveField(
            model_name='oficio',
            name='categories',
        ),
        migrations.AddField(
            model_name='oficio',
            name='categories',
            field=models.ManyToManyField(blank=True, to='oficios.Category'),
        ),
    ]