# Generated by Django 2.0.4 on 2020-05-11 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_auto_20200511_2256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testimonial',
            name='client_name',
            field=models.CharField(default='Satisfied client', max_length=255),
        ),
        migrations.AlterField(
            model_name='testimonial',
            name='testimonial',
            field=models.TextField(blank=True, default=1),
            preserve_default=False,
        ),
    ]