from json import dumps


def collection_to_json(cursor=None):
    if cursor:
        list_cur = list(cursor)
        # json_data = dumps(list_cur, indent=2)
        return list_cur, len(list_cur)
    else:
        return [], 0


def aggregate_to_json(cursor=None, attribute=None):
    result = list(cursor)
    if result and attribute:
        result = result[0][attribute]
        if result:
            return result
        else:
            return []
    else:
        return []
