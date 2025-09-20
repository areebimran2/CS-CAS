import pgtrigger

def set_updated_at_trg(trg_name, timestamp_func="NOW()"):
    """
    Definition for trigger that regularly sets updated_at field to the current timestamp when the table is updated.

    :param trg_name: The name of the trigger.
    :param timestamp_func: The SQL function to get the current timestamp. Default is "now()".
    """
    return pgtrigger.Trigger(
        name=trg_name,
        when=pgtrigger.Before,
        operation=pgtrigger.Update,
        level=pgtrigger.Row,
        func=pgtrigger.Func(
            f"""
            BEGIN
                NEW.updated_at := {timestamp_func};
                RETURN NEW;
            END;
            """
        )
    )