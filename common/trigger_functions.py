import pgtrigger

def set_updated_at(timestamp_func="NOW()"):
    """
    Function definition for triggers to set the updated_at field to the current timestamp.

    :param timestamp_func: The SQL function to get the current timestamp. Default is "now()".
    """
    return pgtrigger.Func(
        f"""
        BEGIN
            NEW.updated_at := {timestamp_func};
            RETURN NEW;
        END;
        """
    )