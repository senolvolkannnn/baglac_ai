# Generated by Django 4.2 on 2025-02-21 01:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("content_manager", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="VisitorSession",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("session_id", models.CharField(max_length=100)),
                ("ip_address", models.GenericIPAddressField()),
                ("user_agent", models.TextField()),
                ("referrer", models.URLField(blank=True, max_length=500, null=True)),
                ("start_time", models.DateTimeField(auto_now_add=True)),
                ("end_time", models.DateTimeField(blank=True, null=True)),
                ("duration", models.PositiveIntegerField(default=0)),
                (
                    "content",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="content_manager.content",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ContentAnalytics",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("views", models.PositiveIntegerField(default=0)),
                ("unique_visitors", models.PositiveIntegerField(default=0)),
                ("avg_time_spent", models.FloatField(default=0.0)),
                ("bounce_rate", models.FloatField(default=0.0)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "content",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="content_manager.content",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Content Analytics",
            },
        ),
        migrations.CreateModel(
            name="DailyMetrics",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                ("views", models.PositiveIntegerField(default=0)),
                ("unique_visitors", models.PositiveIntegerField(default=0)),
                ("total_time_spent", models.PositiveIntegerField(default=0)),
                (
                    "content",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="content_manager.content",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Daily Metrics",
                "unique_together": {("content", "date")},
            },
        ),
    ]
