# Generated by Django 4.1.7 on 2023-04-06 15:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0003_alter_auction_category"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Category",
            new_name="CategoryItem",
        ),
    ]