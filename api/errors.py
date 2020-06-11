def error(code, info=None):
    return {
        'error_code': code,
        'error_info': info,
    }


BAD_USERNAME = error(1, 'Bad username.')
BAD_USER = error(2, 'Bad user.')
BAD_TOKEN = error(19, 'Bad token.')
