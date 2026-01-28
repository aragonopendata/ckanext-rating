import logging

import ckan.model as model
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import sqlalchemy
from ckan.common import c, g
from ckan.lib.plugins import DefaultTranslation
from ckan.plugins import IValidators
from ckan.plugins.toolkit import get_action

from ckanext.rating.logic import auth
from ckanext.rating import helpers
from ckanext.rating.logic import action
from ckanext.rating.model import Rating
from ckanext.rating.views.rating import rating_bp
from .helpers import show_rating_in_type
from .logic import validators

log = logging.getLogger(__name__)


def sort_by_rating(sort):
    limit = g.datasets_per_page
    if c.current_page:
        page = c.current_page
    else:
        page = 1
    offset = (page - 1) * limit
    c.count_pkg = model.Session.query(
        sqlalchemy.func.count(model.Package.id)). \
        filter(model.Package.type == 'dataset'). \
        filter(
        model.Package.private == False  # noqa E712
    ). \
        filter(model.Package.state == 'active').scalar()
    query = model.Session.query(
        model.Package.id, model.Package.title,
        sqlalchemy.func.avg(
            sqlalchemy.func.coalesce(Rating.rating, 0)).
        label('rating_avg')). \
        outerjoin(Rating, Rating.package_id == model.Package.id). \
        filter(model.Package.type == 'dataset'). \
        filter(
        model.Package.private == False  # noqa E712
    ). \
        filter(model.Package.state == 'active'). \
        group_by(model.Package.id). \
        distinct()
    if sort == 'rating desc':
        query = query.order_by(sqlalchemy.desc('rating_avg'))
    else:
        query = query.order_by(sqlalchemy.asc('rating_avg'))
    res = query.offset(offset).limit(limit)
    c.qr = q = [id[0] for id in res]
    tmp = 'id:('
    for id in q:
        tmp += id + ' OR '
    q = tmp[:-4] + ')'
    return q


class RatingPlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(IValidators)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IBlueprint, inherit=True)
    plugins.implements(plugins.IClick)
    if toolkit.check_ckan_version(min_version='2.5.0'):
        plugins.implements(plugins.ITranslation, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('assets', 'rating')

    # IActions

    def get_actions(self):
        return {
            'rtng_create_rating': action.create_rating,
            'rtng_get_rating': action.get_rating,
            'rating_showcase_create': action.create_rating,
            'rating_showcase_get': action.get_rating
        }

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'package_rating': action.get_rating,
            'get_user_rating': helpers.get_user_rating,
            'show_rating_in_type': helpers.show_rating_in_type
        }

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            'rating_auth_user': auth.rating_auth_user,
        }

    # IValidators
    def get_validators(self):
        return {
            'rtng_rating_in_range': validators.rating_in_range,
            'rtng_is_integer': validators.is_integer,
        }

    # IPackageController

    def before_dataset_index(self, data_dict):
        rating_dict = action.get_rating(None, {'package_id': data_dict['id']})
        data_dict['rating'] = rating_dict.get('rating')
        return data_dict

    def after_dataset_show(self, context, pkg_dict):

        if show_rating_in_type(pkg_dict.get('type')):
            rating_dict = get_action('rtng_get_rating')(context, {'package_id': pkg_dict.get('id')})
            pkg_dict['rating'] = rating_dict.get('rating', 0)
            pkg_dict['ratings_count'] = rating_dict.get('ratings_count', 0)
        return pkg_dict

    def after_dataset_search(self, search_results, search_params):

        for pkg in search_results['results']:
            if show_rating_in_type(pkg.get('type')):
                rating_dict = get_action('rtng_get_rating')({}, {'package_id': pkg.get('id')})
                pkg['rating'] = rating_dict.get('rating', 0)
                pkg['ratings_count'] = rating_dict.get('ratings_count', 0)
        return search_results

    # IBlueprint
    def get_blueprint(self):
        return rating_bp

    # IClick
    def get_commands(self):
        from ckanext.rating import cli
        return cli.get_commands()
