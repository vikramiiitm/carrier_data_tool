# Generated by Django 3.2.8 on 2023-01-05 12:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0020_company_docket_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='InsuranceHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form', models.CharField(max_length=20)),
                ('type', models.CharField(max_length=50)),
                ('insurance_carrier', models.CharField(blank=True, max_length=255, null=True)),
                ('policy_surety', models.CharField(blank=True, max_length=100, null=True)),
                ('coverage_from', models.IntegerField()),
                ('coverage_to', models.IntegerField()),
                ('effective_date_from', models.DateField()),
                ('effective_date_to', models.DateField()),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='insurance_history', to='company.company')),
            ],
        ),
    ]