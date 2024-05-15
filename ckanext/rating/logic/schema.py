from ckan.plugins import toolkit as tk


def get_rating_schema() -> dict:
    not_empty = tk.get_validator('not_empty')
    ignore_missing = tk.get_validator('ignore_missing')
    package_id_exists = tk.get_validator('package_id_exists')
    user_id_exists = tk.get_validator('user_id_exists')
    is_integer = tk.get_validator('rtng_is_integer')
    rating_in_range = tk.get_validator('rtng_rating_in_range')

    rating_schema = {
     'package_id': [not_empty, package_id_exists],
     'rating': [not_empty, is_integer, rating_in_range],
     'user_id': [ignore_missing, user_id_exists],
     'rater_ip': [ignore_missing, ],
    }

    return rating_schema