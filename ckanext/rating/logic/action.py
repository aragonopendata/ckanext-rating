import logging

from ckan import model
from ckan.common import _
from ckan.logic import ValidationError
from ckan.model import User
from ckan.plugins import toolkit as tk
from ckan.types import Context, DataDict

from ckanext.rating.model import Rating
from ckanext.rating.logic.schema import get_rating_schema

log = logging.getLogger(__name__)


def _get_user_ip() -> str:
    if tk.request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        user_ip = tk.request.environ.get('REMOTE_ADDR')
    else:
        user = tk.request.environ.get('HTTP_X_FORWARDED_FOR')
        user_ip = user.split(",")[0]
    return user_ip


def create_rating(context: Context, data_dict: DataDict) -> DataDict:
    '''Review a dataset (package).
    :param package: the name or id of the dataset to rate
    :type package: string
    :param rating: the rating to give to the dataset, an integer between 1 and 5
    :type rating: int
    '''
    tk.check_access('rating_auth_user', context, data_dict)
    user = context.get('user')
    rating_schema = get_rating_schema()

    validated_data, errors = tk.navl_validate(data_dict, rating_schema, context)

    user_ip = _get_user_ip()

    context['rater_ip'] = user_ip
    if not user_ip:
        errors['_after'] = [_('Cannot identify user.')]

    user = User.get(user)

    if errors:
        raise ValidationError(errors)

    package_ref = validated_data.get('package')
    package = model.Package.get(package_ref)
    if not package:
        raise ValidationError({'package': [_('Not found: %s') % package_ref]})
    package_id = package.id
    rating = validated_data.get('rating')
    Rating.create(
        package_id=package_id,
        rating=rating,
        rater_ip=user_ip,
        user_id=user.id if user else None
    )

    return Rating.get_rating(package_id)


@tk.side_effect_free
def get_rating(context: Context, data_dict: DataDict):
    '''
    Get the rating and count of ratings for a package.

    Returns a dictionary containing rating and ratings counts.

    :param package_id: the id of the package
    :type package_id: string
    :rtype: dictionary

    '''
    package_id = data_dict.get('package_id')

    error = None

    if not package_id:
        error = _('You must supply a package id '
                  '(parameter "package_id").')
    if error:
        raise ValidationError(error)

    from ckanext.rating.model import Rating

    return Rating.get_rating(package_id)
