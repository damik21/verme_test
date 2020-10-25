# Generated by Django 3.0.7 on 2020-10-25 13:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orgunits', '0002_auto_20201025_1549'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='child', to='orgunits.Organization', verbose_name='Вышестоящая организация'),
        ),
    ]