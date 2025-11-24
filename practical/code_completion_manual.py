# Manual Implementation: Sort list of dicts by specific key

def sort_dicts_by_key(dicts, sort_key):
    return sorted(dicts, key=lambda x: x[sort_key])