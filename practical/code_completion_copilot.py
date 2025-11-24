# Assume this AI-suggested code is produced by Copilot/Tabnine

def sort_dicts_by_key(dicts, key):
    """
    Sort a list of dictionaries by the given key.
    """
    return sorted(dicts, key=lambda d: d.get(key, None))