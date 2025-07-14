import os
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

load_dotenv()

def get_env_variable(var_name):
    value = os.getenv(var_name)
    if value is None:
        raise ImproperlyConfigured(f"Environment variable {var_name} is not set")
    return value
