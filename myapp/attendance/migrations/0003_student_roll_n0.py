# Generated by Django 5.1.3 on 2025-03-07 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0002_remove_studentimage_uploaded_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='roll_n0',
            field=models.CharField(max_length=8, null=True, unique=True),
        ),
    ]
