import pytest
from ckan import model
from ckan.plugins.toolkit import url_for
from sqlalchemy import inspect

from ckanext.rating.model import Rating


@pytest.mark.usefixtures('clean_db')
def test_rating_table_exists(migrate_db_for):
    """Test that the 'rating' table exists."""
    migrate_db_for("rating")
    assert inspect(model.meta.engine).has_table('rating') is True


class TestRatingViews():
    @pytest.mark.usefixtures('clean_db')
    def test_anonymous_user_can_add_rating(self, app, package, user):
        url = url_for("rating.submit_package_rating", package=package['name'], rating="5")
        response = app.get(
            url=url,
            environ_base={'REMOTE_ADDR': '1.1.2.2'}
        )
        assert response.status_code == 200

    @pytest.mark.ckan_config("ckanext.rating.enabled_for_unauthenticated_users", "False")
    @pytest.mark.usefixtures('clean_db')
    def test_anonymous_user_cannot_add_rating_if_disabled(self, app, package, user):
        url = url_for("rating.submit_package_rating", package=package['name'], rating="5")
        response = app.get(
            url=url,
            environ_base={'REMOTE_ADDR': '1.1.2.2'}
        )
        assert response.status_code == 403

    @pytest.mark.usefixtures('clean_db')
    def test_authenticated_user_can_create_rating_with_x_forwarded(self, app, package, user):
        url = url_for("rating.submit_package_rating", package=package['name'], rating="5")
        response = app.get(
            url=url,
            headers={"Authorization": user["token"],
                     "X-Forwarded-For": "1.1.1.1"},
            environ_base={'REMOTE_ADDR': '1.1.2.2'}
        )
        assert response.status_code == 200
        rating = model.Session.query(Rating).filter_by(package_id=package['id'], user_id=user['id']).first()
        assert rating.rating == 5

    @pytest.mark.usefixtures('clean_db')
    def test_authenticated_user_can_create_rating_with_remote_addr(self, app, package, user):
        url = url_for("rating.submit_package_rating", package=package['name'], rating="5")

        response = app.get(
            url=url,
            headers={
                "Authorization": user["token"],
                # "REMOTE_ADDR": "1.1.1.1"
            },
            environ_base={'REMOTE_ADDR': '1.1.2.2'}
        )
        assert response.status_code == 200
        rating = model.Session.query(Rating).filter_by(package_id=package['id'], user_id=user['id']).first()
        assert rating.rating == 5


