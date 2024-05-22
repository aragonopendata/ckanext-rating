import pytest
from ckan.plugins.toolkit import Invalid

from ckanext.rating.model import MIN_RATING, MAX_RATING
from ckanext.rating.logic.validators import rating_in_range


class TestRatingInRange:

    def test_rating_in_range(self):
        assert rating_in_range(MIN_RATING) == MIN_RATING
        assert rating_in_range(3) == 3
        assert rating_in_range(MAX_RATING) == MAX_RATING

    @pytest.mark.parametrize("value", [-1, 0, MIN_RATING - 1, MAX_RATING + 1])
    def test_rating_in_range_raises_error(self, value):
        with pytest.raises(Invalid):
            rating_in_range(value)
