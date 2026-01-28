import ckan.lib.base as base
import ckan.logic as logic
import ckan.model as model
import ckan.plugins as p
from ckan.plugins import toolkit as tk
from ckan.common import request, _
from ckan.lib.base import h
from ckan.views import dataset as dataset_view

from flask import Blueprint

g = tk.g
flatten_to_string_key = logic.flatten_to_string_key
NotAuthorized = logic.NotAuthorized
abort = base.abort

rating_bp = Blueprint('rating', __name__)

@rating_bp.route('/rating/dataset/<package>/<rating>')
def submit_package_rating(package, rating):
    context = {'model': model, 'user': g.user or g.author}
    data_dict = {'package': package, 'rating': rating}
    try:
        tk.get_action('rtng_create_rating')(context, data_dict)
        return h.redirect_to('dataset.read', id=package)
    except NotAuthorized:
        abort(403, _('Unauthenticated user not allowed to submit ratings.'))


@rating_bp.route('/rating/showcase/<package>/<rating>')
def submit_showcase_rating(package, rating):
    context = {'model': model, 'user': g.user or g.author}
    data_dict = {'package': package, 'rating': rating}
    try:
        tk.check_access('rating_auth_user', context, data_dict)
        tk.get_action('rtng_create_rating')(context, data_dict)
        h.redirect_to('sixodp_showcase.read', id=package)
    except NotAuthorized:
        abort(403, _('Unauthenticated user not allowed to submit ratings.'))


@rating_bp.route('/dataset')
def search():
    cur_page = request.args.get('page')
    if cur_page is not None:
        g.current_page = h.get_page_number(request.args)
    else:
        g.current_page = 1
    g.pkg_type = 'dataset'
    result = dataset_view.search(package_type=g.pkg_type)
    return result



