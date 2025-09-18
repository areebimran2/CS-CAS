from django.db import models

class PostgresEnumField(models.Field):
    """
    A custom Django model field to represent a Postgres ENUM type.

    Django does not have built-in support for native DB ENUM types. Hence,
    this custom field facilitates the translation between Django and Postgres ENUMs.
    """
    description = "Postgres ENUM field"

    def __init__(self, enum_type, choices=None, **kwargs):
        self.enum_type = enum_type  # The name of the Postgres ENUM type
        super().__init__(choices=choices, **kwargs)

    def db_type(self, connection):
        return self.enum_type

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["enum_type"] = self.enum_type
        return name, path, args, kwargs