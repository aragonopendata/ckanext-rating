import factory
from ckan.model import Session
from ckan.tests.factories import CKANFactory
from faker import Faker

import ckan.logic
from ckanext.rating.model import Rating

fake = Faker()


class RatingFactory(CKANFactory):
    """A factory class for creating CKAN datasets."""

    class Meta:
        # model is model.Rating from this plugin
        model = Rating
        action = "rating_create"
    # assert Session.query(ckan.model.Package).all() != []
    package_id = factory.LazyFunction(lambda: Session.query(ckan.model.Package).first().id)

    rating = factory.LazyFunction(lambda: fake.random_int(min=1, max=5))
    user_id = 1
    rater_ip = factory.LazyFunction(lambda: fake.ipv4())

