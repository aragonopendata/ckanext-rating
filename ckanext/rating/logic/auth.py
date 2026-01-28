from ckan.plugins.toolkit import config, asbool, auth_allow_anonymous_access, g


@auth_allow_anonymous_access
def rating_auth_user(context, data_dict):
    if hasattr(g, 'user') and g.user:
        return {'success': True}
    else:
        allow_rating = asbool(
            config.get('ckanext.rating.enabled_for_unauthenticated_users', True))
    return {'success': allow_rating}
