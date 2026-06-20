def positive_int_query(query_params, name, default, maximum=None):
    try:
        value = int(query_params.get(name, default))
    except (TypeError, ValueError):
        return default
    if value < 1:
        return default
    if maximum is not None:
        return min(value, maximum)
    return value


def optional_positive_int(value):
    if value in (None, ""):
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    if parsed < 1:
        return None
    return parsed


def non_negative_int(value, default=0):
    try:
        parsed = int(value if value not in (None, "") else default)
    except (TypeError, ValueError):
        return default
    return max(parsed, 0)


def positive_int_list(values):
    if not isinstance(values, list):
        return None
    parsed_values = []
    seen = set()
    for value in values:
        parsed = optional_positive_int(value)
        if parsed is None:
            return None
        if parsed not in seen:
            parsed_values.append(parsed)
            seen.add(parsed)
    return parsed_values


def positive_int_sequence(values):
    if not isinstance(values, list):
        return None
    parsed_values = []
    for value in values:
        parsed = optional_positive_int(value)
        if parsed is None:
            return None
        parsed_values.append(parsed)
    return parsed_values


def positive_int_csv(value):
    if isinstance(value, list):
        return positive_int_list(value)
    if value in (None, ""):
        return []
    return positive_int_list([part.strip() for part in str(value).split(",")])
