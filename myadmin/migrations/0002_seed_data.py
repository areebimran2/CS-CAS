from django.db import migrations


class Migration(migrations.Migration):
    """Seed the default roles and permissions (db.html section 16)."""

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
        # -- Permissions (sample; expand as needed)
        migrations.RunSQL(
            """
            INSERT INTO permissions(key, description) VALUES
                ('realtime.subscribe','Subscribe to realtime WS'),
                ('lock.override','Override collaborative locks'),
                ('pricing.override_margin','Override default margins'),
                ('discount.activate','Activate or deactivate discounts')
            ON CONFLICT DO NOTHING;
            """,
            reverse_sql="""
            DELETE FROM permissions
                WHERE key IN ('realtime.subscribe','lock.override','pricing.override_margin','discount.activate');
            """
        ),
    ]
