from rest_framework.views import exception_handler


def _get_key(response, field):
    if isinstance(response.data[field], list):
        return response.data[field][0]
    else:
        return response.data[field]


def _prettify_result(error_message):
    if (error_message['error_key'] == 'must_be_unique' and
            error_message['error_fields'] and
            error_message['error_fields'][0] == 'username'
    ):
        error_message['error_key'] = 'username_taken'
        error_message['error_fields'] = []


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    error_key = ''
    error_fields = []

    for field in reversed(response.data):
        if field not in ['detail', 'non_field_errors']:
            error_key = _get_key(response, field)
            error_fields = [field]

    if 'detail' in response.data:
        error_key = _get_key(response, 'detail')
    if 'non_field_errors' in response.data:
        error_key = _get_key(response, 'non_field_errors')

    if '|' in error_key:
        split = error_key.split('|')
        error_key = split[0]
        error_fields = split[1].split(', ')

    error_message = {
        'error_key': error_key,
        'error_fields': error_fields,
    }

    _prettify_result(error_message)
    response.data = error_message

    return response
