import logging

from ckan.common import _
from ckan.logic import ValidationError
from ckan.plugins import toolkit as tk

from ckanext.rating.model import Rating
from rating.logic.schema import get_rating_schema
from ckan.types import Context, DataDict
from ckan.model import User

log = logging.getLogger(__name__)


def create_rating(context: Context, data_dict: DataDict) -> DataDict:
    '''Review a dataset (package).
    :param package: the name or id of the dataset to rate
    :type package: string
    :param rating: the rating to give to the dataset, an integer between 1 and 5
    :type rating: int
    '''
    # model = context.get('model')
    user = context.get('user')
    user_ip = context.get('rater_ip')
    rating_schema = get_rating_schema()

    validated_data, errors = tk.navl_validate(data_dict, rating_schema, context)
    # model = validated_data.get('model')
    # user = validated_data.get('user')

    # user = User.by_name(user)
    user = User.get(user)

    if not user_ip and not user:
        errors['_after'] = [_('Cannot determine user or ip. Please log in.')]

    if errors:
        raise ValidationError(errors)



    # if not isinstance(user, User):
    # TODO: Get user ip address
        # if tk.request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        #     user = tk.request.environ.get('REMOTE_ADDR')
        # else:
        #     user = tk.request.environ.get('HTTP_X_FORWARDED_FOR')
        #     user_ip = user.split(",")[0]
        #     user = user_ip

    # package_ref = data_dict.get('package_id')
    # rating = data_dict.get('rating')
    # error = None
    # if not package_ref:
    #     error = _('You must supply a package id or name '
    #               '(parameter "package").')
    # elif not rating:
    #     error = _('You must supply a rating (parameter "rating").')
    # else:
    #     try:
    #         rating = float(rating)
    #     except ValueError:
    #         error = _('Rating must be an integer value.')
    #     else:
    #         package = Package.get(package_ref)
    #         if rating < MIN_RATING or rating > MAX_RATING:
    #             error = _('Rating must be between %i and %i.') \
    #                     % (MIN_RATING, MAX_RATING)
    #         elif not package:
    #             error = _('Not found') + ': %r' % package_ref
    # if error:
    #     raise ValidationError(error)

    package_id = validated_data.get('package_id')
    rating = validated_data.get('rating')
    Rating.create(
        package_id=package_id,
        rating=rating,
        rater_ip=user_ip,
        user_id=user.id
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
