# Generated by Django 3.2.15 on 2022-09-01 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tags',
            name='color',
            field=models.CharField(default='ffffff', max_length=6),
        ),
    ]
