# Generated by Django 4.2 on 2024-07-09 14:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Industry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization_id', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=255)),
                ('website', models.URLField()),
                ('description', models.CharField(max_length=255)),
                ('year_founded', models.IntegerField()),
                ('number_of_employees', models.IntegerField()),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.country')),
                ('industry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.industry')),
            ],
        ),
        migrations.DeleteModel(
            name='Company',
        ),
    ]
