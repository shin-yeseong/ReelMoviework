# Generated by Django 4.1.13 on 2024-11-11 07:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0003_alter_contactinfo_user_alter_registrationinfo_user_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contactinfo",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="common.user",
            ),
        ),
        migrations.AlterField(
            model_name="registrationinfo",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="common.user",
            ),
        ),
        migrations.AlterField(
            model_name="securityinfo",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="common.user",
            ),
        ),
    ]
