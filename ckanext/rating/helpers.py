from ckanext.rating.model import Rating
from ckan.plugins import toolkit
from ckan.common import config

from ckanext.rating.logic.action import _get_user_ip

c = toolkit.c


def get_user_rating(package_id):
    user = c.userobj
    rater_ip = _get_user_ip()
    # if not c.userobj:
    #     user = toolkit.request.environ.get('REMOTE_ADDR')
    # else:
    #     user = c.userobj
    user_rating = Rating.get_user_rating(
        package_id=package_id,
        user_id=user.id if user else None,
        rater_ip=rater_ip
    )
    return user_rating.rating if user_rating is not None else None


def show_rating_in_type(type):
    return type in config.get('ckanext.rating.enabled_dataset_types',
                              ['dataset'])
