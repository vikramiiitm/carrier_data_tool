# Generated by Django 3.2.8 on 2022-11-30 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0003_basics_basicsentity_cargocarried_inspection_licensingandinsurence_operationclasfication'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='dba',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
