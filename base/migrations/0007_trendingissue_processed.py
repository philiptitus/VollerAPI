# Generated by Django 4.2.15 on 2024-09-26 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_remove_trendingissue_first_analysis_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='trendingissue',
            name='processed',
            field=models.BooleanField(default=False),
        ),
    ]
