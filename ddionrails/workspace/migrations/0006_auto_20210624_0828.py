# Generated by Django 3.2.4 on 2021-06-24 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("workspace", "0005_auto_20200608_0702")]

    operations = [
        migrations.AlterField(
            model_name="basket",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="basketvariable",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="script",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]