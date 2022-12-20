# Generated by Django 3.2.8 on 2022-12-07 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0010_auto_20221202_1539'),
    ]

    operations = [
        migrations.CreateModel(
            name='InspectionAndSafetyMeasures',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hazmat', models.CharField(choices=[('H', 'HAZMAT'), ('N', 'NON_HAZMAT')], default='H', max_length=20)),
                ('inspection_total', models.IntegerField(blank=True, null=True)),
                ('driver_inspection_total', models.IntegerField(blank=True, null=True)),
                ('driver_oos_inspection_total', models.IntegerField(blank=True, null=True)),
                ('vehicle_inspection_total', models.IntegerField(blank=True, null=True)),
                ('vehicle_oos_inspection_total', models.IntegerField(blank=True, null=True)),
                ('unsafe_driver_inspection_violation', models.IntegerField(blank=True, null=True)),
                ('unsafe_driver_measure', models.IntegerField(blank=True, null=True)),
                ('hos_driver_inspection_violation', models.IntegerField(blank=True, null=True)),
                ('hos_driver_measure', models.IntegerField(blank=True, null=True)),
                ('driver_fit_inspection_violation', models.IntegerField(blank=True, null=True)),
                ('driver_fit_measure', models.IntegerField(blank=True, null=True)),
                ('contr_subst_inspection_violation', models.IntegerField(blank=True, null=True)),
                ('contr_subst_measure', models.IntegerField(blank=True, null=True)),
                ('vehicle_maintenance_violation', models.IntegerField(blank=True, null=True)),
                ('vehicle_maintenance_measure', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.DeleteModel(
            name='Inspection',
        ),
    ]
