import pytest
from ckan.logic import get_action, ValidationError
from ckan.tests import factories

from ckanext.rating.model import Rating


@pytest.fixture
def user():
    return factories.User()


@pytest.fixture
def package(user):
    return factories.Dataset(user=user)


@pytest.mark.usefixtures('clean_db', autouse=True)
def test_can_get_package_rating_with_valid_package(user, package):
    context = {'user': user['name']}
    data_dict = {'package_id': package['id']}
    get_rating = get_action('rtng_get_rating')
    result = get_rating(context, data_dict)
    assert isinstance(result, dict)
    assert 'rating' in result
    assert 'ratings_count' in result


def test_cannot_get_package_rating_with_invalid_package(user):
    context = {'user': user['name']}
    data_dict = {'package_id': 'invalid_package'}
    get_rating = get_action('rtng_get_rating')
    with pytest.raises(ValidationError):
        get_rating(context, data_dict)


def test_cannot_get_package_rating_without_package(user):
    context = {'user': user['name']}
    data_dict = {}
    get_rating = get_action('rtng_get_rating')
    with pytest.raises(ValidationError):
        get_rating(context, data_dict)
