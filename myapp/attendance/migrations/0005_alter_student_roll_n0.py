# Generated by Django 5.1.3 on 2025-03-07 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0004_alter_student_roll_n0'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='roll_n0',
            field=models.CharField(blank=True, max_length=8, null=True, unique=True),
        ),
    ]
