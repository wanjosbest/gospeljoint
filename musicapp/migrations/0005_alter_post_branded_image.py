# Generated by Django 5.2 on 2025-05-10 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicapp', '0004_post_lyrics'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='branded_image',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
