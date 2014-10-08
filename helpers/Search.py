def search_dict(my_dict, field):
    """Takes a dict with nested lists and dicts,
    and searches all dicts for a key of the field
    provided.
    """
    fields_found = []

    for key, value in my_dict.iteritems():

        if key == field:
            fields_found.append(value)

        elif isinstance(value, dict):
            results = search_dict(value, field)
            for result in results:
                fields_found.append(result)

        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    more_results = search_dict(item, field)
                    for another_result in more_results:
                        fields_found.append(another_result)

    return fields_found