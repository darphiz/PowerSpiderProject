import re

def reverse_list(string):
    if not string:
        return []
    return re.findall(r'"([^"]*)"', string)

def format_list(lists):
    try:
        if not lists:
            return None
        if not isinstance(lists, list):
            lists = [lists]
        _set = {"\"" + x + "\"" for x in lists}
        _set = str(_set).replace("'", "")
        return _set
    except Exception:
        return None

def pipe_list(list_one, list_two):
    rev_one = reverse_list(list_one)
    rev_two = reverse_list(list_two)
    joint_list = rev_one + rev_two
    unique_list = list(set(joint_list))
    return format_list(unique_list)
