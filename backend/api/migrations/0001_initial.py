# Generated by Django 4.2 on 2024-07-08 05:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('website', models.URLField(max_length=50)),
                ('foundation', models.PositiveIntegerField()),
            ],
        ),
    ]
