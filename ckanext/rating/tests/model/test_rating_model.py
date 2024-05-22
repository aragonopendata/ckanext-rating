from unittest import mock

import pytest
from ckan import model
from ckan.tests import factories
from faker import Faker
from sqlalchemy import inspect

from ckanext.rating.model import Rating


@pytest.fixture
def ip():
    faker = Faker()
    return faker.ipv4()


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


class TestRatingMocked:
    @mock.patch('ckanext.rating.model.Rating.save')
    def test_create_review(self, mock_save):
        # Mock the database session
        # Rating.save = MagicMock()

        # Test data
        package_id = "test_package"
        rating = 4
        user_id = "test_user"
        rater_ip = "192.168.1.1"

        # Call the method
        Rating._create_review(package_id, rating, user_id, rater_ip)

        # Assert that the save method was called on the Rating object
        mock_save.assert_called_once()

    @mock.patch('ckanext.rating.model.Rating.save')
    def test_create_review_no_user_id_or_ip(self, mock_save):
        # Mock the database session

        # Test data
        package_id = "test_package"
        rating = 4.5

        # Call the method and assert that it raises a ValueError
        with pytest.raises(ValueError):
            Rating._create_review(package_id, rating)


class TestRating:

    @pytest.mark.usefixtures('clean_db', autouse=True)
    def test_create_rating_with_package_id_and_user_id(self, package, user, ip):
        ratings_before = model.Session.query(Rating).count()
        Rating.create(package_id=package['id'], user_id=user['id'], rating=3, rater_ip=ip)
        ratings_after = model.Session.query(Rating).count()
        assert ratings_after == ratings_before + 1
        new_rating = model.Session.query(Rating).filter(Rating.package_id == package['id']).first()
        assert new_rating.rating == 3
        assert new_rating.user_id == user['id']
        assert new_rating.rater_ip == ip

    def test_create_rating_with_package_id_and_ip(self, package, ip):
        ratings_before = model.Session.query(Rating).count()
        Rating.create(package_id=package['id'], rating=3, rater_ip=ip)
        ratings_after = model.Session.query(Rating).count()
        assert ratings_after == ratings_before + 1
        new_rating = model.Session.query(Rating).filter(Rating.package_id == package['id']).first()
        assert new_rating.rating == 3
        assert new_rating.user_id is None
        assert new_rating.rater_ip == ip

    def test_create_rating_when_rating_exists(self, package, user, ip):
        Rating.create(package_id=package['id'], user_id=user['id'], rating=3, rater_ip=ip)
        ratings_before = model.Session.query(Rating).count()
        Rating.create(package_id=package['id'], user_id=user['id'], rating=4, rater_ip=ip)
        ratings_after = model.Session.query(Rating).count()
        assert ratings_after == ratings_before
        updated_rating = model.Session.query(Rating).filter(Rating.package_id == package['id']).first()
        assert updated_rating.rating == 4
        assert updated_rating.user_id == user['id']
        assert updated_rating.rater_ip == ip
