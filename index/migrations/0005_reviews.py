# Generated by Django 2.2.3 on 2019-08-09 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0004_auto_20190809_1115'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reviews',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business_id', models.CharField(max_length=84)),
                ('username', models.CharField(max_length=84)),
                ('image_url', models.CharField(max_length=100, null=True)),
                ('review_text', models.TextField()),
                ('timestamp', models.CharField(max_length=200)),
            ],
        ),
    ]
