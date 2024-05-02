import ckan.lib.base as base
import ckan.logic as logic
import ckan.model as model
import ckan.plugins as p
from ckan.common import request, _
from ckan.lib.base import h
from ckan.views import dataset as dataset_view

from flask import Blueprint

c = p.toolkit.c
flatten_to_string_key = logic.flatten_to_string_key
NotAuthorized = logic.NotAuthorized
abort = base.abort

rating_bp = Blueprint('rating', __name__)

@rating_bp.route('/rating/dataset/<package>/<rating>')
def submit_package_rating(package, rating):
    context = {'model': model, 'user': c.user or c.author}
    data_dict = {'package': package, 'rating': rating}
    try:
        p.toolkit.check_access('check_access_user', context, data_dict)
        p.toolkit.get_action('rating_package_create')(context, data_dict)
        h.redirect_to(controller='package', action='read', id=package)
    except NotAuthorized:
        abort(403, _('Unauthenticated user not allowed to submit ratings.'))


@rating_bp.route('/rating/showcase/<package>/<rating>')
def submit_showcase_rating(package, rating):
    context = {'model': model, 'user': c.user or c.author}
    data_dict = {'package': package, 'rating': rating}
    try:
        p.toolkit.check_access('check_access_user', context, data_dict)
        p.toolkit.get_action('rating_package_create')(context, data_dict)
        h.redirect_to('sixodp_showcase.read', id=package)
    except NotAuthorized:
        abort(403, _('Unauthenticated user not allowed to submit ratings.'))


@rating_bp.route('/dataset')
def search():
    cur_page = request.params.get('page')
    if cur_page is not None:
        c.current_page = h.get_page_number(request.params)
    else:
        c.current_page = 1
    c.pkg_type = 'dataset'
    result = dataset_view.search(package_type=c.pkg_type)
    return result



