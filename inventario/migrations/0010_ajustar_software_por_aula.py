from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("infraestructura", "0001_initial"),
        ("inventario", "0009_alter_softwareinstalado_options_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="softwareinstalado",
            name="computador",
        ),
        migrations.AlterField(
            model_name="softwareinstalado",
            name="aula",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="software_instalado",
                to="infraestructura.aula",
            ),
        ),
        migrations.AddConstraint(
            model_name="softwareinstalado",
            constraint=models.UniqueConstraint(
                fields=("aula", "nombre"),
                name="unique_software_por_aula",
            ),
        ),
    ]
