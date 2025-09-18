from django.db import models

class TxNow(models.Func):
    """
    Represents the PostgreSQL NOW() function, which returns the current timestamp.
    Django's built-in Now() function translates to STATEMENT_TIMESTAMP() at the DB level.

    Created to ensure consistency at the DB level for default timestamp values.
    """
    function = 'NOW'
    template = '%(function)s()'
    output_field = models.DateTimeField()