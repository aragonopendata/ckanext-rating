"""Tests for plugin.py."""

import ckan.model as model
import ckan.tests.factories as factories
import pytest
from ckan.plugins import toolkit as tk
from sqlalchemy import inspect

from ckanext.rating.model import Rating, init_tables
from rating.tests.factories import RatingFactory

__ALL__ = ['TestBase']


@pytest.fixture(autouse=True)
def with_rating_table():
    """Fixture to add the rating table to the database."""
    init_tables(engine=model.meta.engine)
    yield


def test_rating_plugin_loaded():
    """Test that the rating plugin is loaded."""
    plugins = tk.config.get("ckan.plugins")
    assert "rating" in plugins


@pytest.mark.usefixtures('clean_db')
def test_rating_table_created(with_rating_table):
    """Test that the 'review' table exists."""
    assert 'rating' in tk.config.get('ckan.plugins'), 'Rating plugin not enabled'
    # init_tables(engine=model.meta.engine)
    engine = model.meta.engine
    # Test that the database is initialized
    assert inspect(engine).has_table('package') is True
    # Then test that the table is created
    assert inspect(engine).has_table('review') is True, "Table 'review' not created"


@pytest.mark.usefixtures('clean_db')
class TestBase:

    def test_2(self):
        user = factories.User()
        admin_user = model.User.get("testsysadmin")
        owner_org = factories.Organization(users=[{
            'name': user['id'],
            'capacity': 'member'
        }])
        num_packages = model.Session.query(model.Package).all()
        assert len(num_packages) == 0
        dataset = factories.Dataset(owner_org=owner_org['id'], id=None)
        num_packages = model.Session.query(model.Package).all()
        assert len(num_packages) == 1

    def test_rating_factory(self):
        dataset_dict = factories.Dataset()
        d = model.Package.get(dataset_dict['id'])
        pkgs_db = [pid for pid, in model.Session.query(model.Package.id).all()]
        assert d.id in pkgs_db
        num_ratings_before = len(model.Session.query(Rating).all())
        # rating = RatingFactory(package_id=d.id)
        rating = RatingFactory()
        num_ratings_after = len(model.Session.query(Rating).all())
        assert num_ratings_after == num_ratings_before + 1
