# Generated by Django 3.2.8 on 2022-12-28 10:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0016_alter_inspectionandsafetymeasures_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operationclasfication',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='operaton_classfication', to='company.company'),
        ),
    ]