from typing import Optional

from ckan.types import FlattenKey, FlattenDataDict, FlattenErrorDict, Context

from ckanext.rating.model import MIN_RATING, MAX_RATING
from ckan.plugins.toolkit import Invalid, StopOnError, _


def rating_in_range(value):
    """Validate that the rating is within the allowed range. MAX_RATING >= rating >= MIN_RATING"""
    if value < MIN_RATING or value > MAX_RATING:
        raise Invalid(_(f'Rating must be between {MIN_RATING} and {MAX_RATING}'))
    return value


def is_integer(key: FlattenKey, data: FlattenDataDict,
                 errors: FlattenErrorDict, context: Context) -> None:

    if not isinstance(data[key], int):
        errors[key] = [_('Value is not an integer')]
        raise StopOnError
