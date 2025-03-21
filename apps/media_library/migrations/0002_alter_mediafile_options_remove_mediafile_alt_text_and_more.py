# Generated by Django 4.2 on 2025-02-21 02:21

import apps.media_library.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("media_library", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="mediafile",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Medya Dosyası",
                "verbose_name_plural": "Medya Dosyaları",
            },
        ),
        migrations.RemoveField(
            model_name="mediafile",
            name="alt_text",
        ),
        migrations.RemoveField(
            model_name="mediafile",
            name="category",
        ),
        migrations.AlterField(
            model_name="mediafile",
            name="file",
            field=models.FileField(upload_to=apps.media_library.models.upload_to),
        ),
        migrations.AlterField(
            model_name="mediafile",
            name="file_size",
            field=models.IntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name="mediafile",
            name="file_type",
            field=models.CharField(
                choices=[
                    ("image", "Görsel"),
                    ("video", "Video"),
                    ("document", "Doküman"),
                    ("other", "Diğer"),
                ],
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="mediafile",
            name="mime_type",
            field=models.CharField(editable=False, max_length=100),
        ),
    ]
