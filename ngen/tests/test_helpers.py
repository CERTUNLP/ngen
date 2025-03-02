from constance.test import override_config
from functools import wraps


def use_test_email_env():
    """
    Override constance config to use test email environment values
    """

    def decorator(func):
        @wraps(func)
        @override_config(EMAIL_HOST="ngen-mail")
        @override_config(EMAIL_SENDER="test@ngen.com")
        @override_config(EMAIL_USERNAME="username")
        @override_config(EMAIL_PASSWORD="password")
        @override_config(EMAIL_PORT="1025")
        @override_config(EMAIL_USE_TLS=False)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def use_incorrect_email_env():
    """
    Override constance config to use incorrent test email environment values
    """

    def decorator(func):
        @wraps(func)
        @override_config(EMAIL_HOST="localhost")
        @override_config(EMAIL_SENDER="test@example.com")
        @override_config(EMAIL_USERNAME="username")
        @override_config(EMAIL_PASSWORD="password")
        @override_config(EMAIL_PORT="9999")
        @override_config(EMAIL_USE_TLS=False)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator
