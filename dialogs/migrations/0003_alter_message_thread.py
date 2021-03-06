# Generated by Django 3.2.3 on 2021-06-27 18:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("dialogs", "0002_auto_20210612_1115"),
    ]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="thread",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="thread_messages",
                to="dialogs.thread",
            ),
        ),
    ]
