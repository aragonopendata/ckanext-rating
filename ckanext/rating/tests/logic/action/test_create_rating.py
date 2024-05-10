import pytest
from ckan import model
from ckan.logic import get_action, ValidationError
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


@pytest.mark.usefixtures('clean_db', autouse=True)
def test_can_create_rating_with_valid_data(user, package):
    """A user can create a rating for an existing package."""
    context = {'user': user['name']}
    data_dict = {'package_id': package['id'], 'rating': 3}

    ratings_before = model.Session.query(Rating).count()
    result = helpers.call_action('rtng_create_rating', context, **data_dict)
    ratings_after = model.Session.query(Rating).count()

    assert result['rating'] == 3
    assert ratings_after == ratings_before + 1


def test_create_rating_updates_existing_rating(user, package):
    """If a user rates a package they have already rated, the rating should be updated."""
    context = {'user': user['name']}
    data_dict = {'package_id': package['id'], 'rating': 3}

    helpers.call_action('rtng_create_rating', context, **data_dict)
    ratings_before = model.Session.query(Rating).count()

    data_dict['rating'] = 4
    result = helpers.call_action('rtng_create_rating', context, **data_dict)
    ratings_after = model.Session.query(Rating).count()

    assert result['rating'] == 4
    assert ratings_after == ratings_before


#TODO: Test the case where the user is not logged in.
# @pytest.mark.xfail(
#     reason="This test fails because I don't know how to pass the IP address but not a user to the action.")
@pytest.mark.usefixtures('with_request_context')
def test_create_rating_with_no_user_but_ip(package):
    """If a user rates a package without being logged in, the rating should be saved with their IP address."""
    context = {'user': None, 'HTTP_X_FORWARDED_FOR': '1.1.1.1'}
    data_dict = {'package_id': package['id'], 'rating': 3}
    ratings_before = model.Session.query(Rating).count()
    del context['user']
    result = helpers.call_action('rtng_create_rating', context, **data_dict)
    ratings_after = model.Session.query(Rating).count()

    assert result['rating'] == 3
    assert ratings_after == ratings_before + 1


def test_cannot_create_rating_with_invalid_package(user):
    """With an invalid package ID, the action should raise a ValidationError.   """
    context = {'user': user['name']}
    data_dict = {'package_id': 'invalid_package', 'rating': 3}

    create_rating = get_action('rtng_create_rating')
    with pytest.raises(ValidationError):
        create_rating(context, data_dict)


@pytest.mark.parametrize('rating', [0, -1, MAX_RATING + 1, 1.5, '3'])
def test_cannot_create_rating_with_invalid_rating(user, package, rating):
    """With an invalid rating, the action should raise a ValidationError."""
    context = {'user': user['name']}
    data_dict = {'package_id': package['id'], 'rating': MAX_RATING + 1}
    create_rating = get_action('rtng_create_rating')
    with pytest.raises(ValidationError):
        create_rating(context, data_dict)
