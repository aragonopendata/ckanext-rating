import pytest
from ckan.tests import factories


@pytest.fixture
def user():
    return factories.UserWithToken()


@pytest.fixture
def package(user):
    return factories.Dataset(user=user)
