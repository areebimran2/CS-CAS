from django.db import migrations


class Migration(migrations.Migration):
    """Seed the default cabin categories and reserve settings (db.html section 16)."""

    dependencies = [
        ('catalogs', '0001_initial'),
    ]

    operations = [
        # -- Cabin categories
        migrations.RunSQL(
            """
            INSERT INTO cabin_categories(name, sort_order) VALUES
                ('Inside',10),('Oceanview',20),('Balcony',30),('Suite',40),('Deluxe',50),('Premium',60)
            ON CONFLICT DO NOTHING;
            """,
            reverse_sql="""
            DELETE FROM cabin_categories
                WHERE name IN ('Inside','Oceanview','Balcony','Suite','Deluxe','Premium');
            """
        ),
        # -- Reserve settings (default). Inserted only if none exist, so re-running is harmless.
        migrations.RunSQL(
            """
            INSERT INTO reserve_settings(id)
                SELECT gen_random_uuid() WHERE NOT EXISTS (SELECT 1 FROM reserve_settings);
            """,
            # The row has a random id, so it can't be targeted on reverse. Reversing 0001 drops the table anyway.
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
