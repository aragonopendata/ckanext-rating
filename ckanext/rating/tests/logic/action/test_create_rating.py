import pytest
from ckan import model
from ckan.plugins.toolkit import ValidationError, get_action, g, request
from ckan.tests import factories, helpers
from sqlalchemy import inspect

from ckanext.rating.model import MAX_RATING, Rating


@pytest.fixture
def user():
    return factories.User()


@pytest.fixture
def package(user):
    return factories.Dataset(user=user)


@pytest.mark.usefixtures('clean_db')
def test_rating_table_exists(migrate_db_for):
    """Test that the 'rating' table exists."""
    migrate_db_for("rating")
    assert inspect(model.meta.engine).has_table('rating') is True


@pytest.mark.usefixtures('with_request_context')
@pytest.mark.usefixtures('clean_db', autouse=True)
def test_can_create_rating_with_valid_data(user, package):
    """A user can create a rating for an existing package."""
    context = {'user': user['id']}
    data_dict = {'package': package['id'], 'rating': 3}
    # request_context['user'] = user['id']
    g.user = user['id']
    request.environ['REMOTE_ADDR'] = '1.1.2.2'
    context['rater_ip'] = "1.1.1.1"
    ratings_before = model.Session.query(Rating).count()
    action = get_action('rtng_create_rating')
    result = action(context, data_dict)
    # result = helpers.call_action('rtng_create_rating', context, **data_dict)
    ratings_after = model.Session.query(Rating).count()

    assert result['rating'] == 3
    assert ratings_after == ratings_before + 1

@pytest.mark.usefixtures('with_request_context')
def test_create_rating_updates_existing_rating(user, package):
    """If a user rates a package they have already rated, the rating should be updated."""
    context = {'user': user['name']}
    data_dict = {'package': package['id'], 'rating': 3}
    request.environ['REMOTE_ADDR'] = '1.1.2.2'

    helpers.call_action('rtng_create_rating', context, **data_dict)
    ratings_before = model.Session.query(Rating).count()

    data_dict['rating'] = 4
    g.user = user['id']
    result = helpers.call_action('rtng_create_rating', context, **data_dict)
    ratings_after = model.Session.query(Rating).count()

    assert result['rating'] == 4
    assert ratings_after == ratings_before


@pytest.mark.usefixtures('with_request_context')
def test_create_rating_with_no_user_but_ip(package):
    """If a user rates a package without being logged in, the rating should be saved with their IP address."""
    context = {'user': None}
    request.environ['REMOTE_ADDR'] = '1.1.2.2'
    data_dict = {'package': package['id'], 'rating': 3}
    ratings_before = model.Session.query(Rating).count()
    del context['user']

    action = get_action('rtng_create_rating')
    result = action(context, data_dict)
    ratings_after = model.Session.query(Rating).count()

    assert result['rating'] == 3
    assert ratings_after == ratings_before + 1

@pytest.mark.usefixtures('with_request_context')
def test_cannot_create_rating_with_invalid_package(user):
    """With an invalid package ID, the action should raise a ValidationError.   """
    context = {'user': user['name']}
    data_dict = {'package': 'invalid_package', 'rating': 3}

    g.user = user['id']
    request.environ['REMOTE_ADDR'] = '1.1.2.2'

    create_rating = get_action('rtng_create_rating')
    with pytest.raises(ValidationError):
        create_rating(context, data_dict)

@pytest.mark.usefixtures('with_request_context')
@pytest.mark.parametrize('rating', [0, -1, MAX_RATING + 1, 1.5, 'a', None, ''])
def test_cannot_create_rating_with_invalid_rating(user, package, rating):
    """With an invalid rating, the action should raise a ValidationError."""
    context = {'user': user['name']}
    data_dict = {'package': package['id'], 'rating': rating}

    g.user = user['id']
    request.environ['REMOTE_ADDR'] = '1.1.2.2'
    create_rating = get_action('rtng_create_rating')
    with pytest.raises(ValidationError):
        create_rating(context, data_dict)
