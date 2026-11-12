from django.db import migrations


class Migration(migrations.Migration):
    """
    Seed the default roles (db.html section 16). Permissions are not seeded here: they come from
    common/permissions.py, which myadmin copies into the table after every migrate (see myadmin/apps.py).
    """

    dependencies = [
        ('myadmin', '0001_initial'),
    ]

    operations = [
        # -- Roles
        migrations.RunSQL(
            """
            INSERT INTO roles(name, description) VALUES
                ('Admin','Full access'),
                ('Pricing Manager','Manage pricing & discounts'),
                ('Sales','Reserve & book'),
                ('Operations','Ships, routes, sailings'),
                ('Read-only','View only')
            ON CONFLICT DO NOTHING;
            """,
            reverse_sql="""
            DELETE FROM roles
                WHERE name IN ('Admin','Pricing Manager','Sales','Operations','Read-only');
            """
        ),
    ]
