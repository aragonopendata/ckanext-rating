import datetime
import uuid
from typing import Optional

import ckan.model as model
from ckan.lib import dictization
from ckan.model import User
from ckan.model.base import ActiveRecordMixin, DebugMixin
from sqlalchemy import types, Column, UniqueConstraint
from sqlalchemy.orm import declarative_base

log = __import__('logging').getLogger(__name__)

Base = declarative_base(metadata=model.meta.metadata)

__all__ = ['MIN_RATING', 'MAX_RATING', 'Rating']

MIN_RATING = 1.0
MAX_RATING = 5.0


def make_uuid():
    return str(uuid.uuid4())


class Rating(Base, DebugMixin, ActiveRecordMixin):
    __tablename__ = 'review'

    id = Column(types.UnicodeText, primary_key=True, default=make_uuid)
    package_id = Column(types.UnicodeText, index=True)
    rating = Column(types.Float)
    user_id = Column(types.UnicodeText, nullable=True, index=True)
    rater_ip = Column(types.UnicodeText, index=True)  # Used for identification if user is not authenticated
    created = Column(types.DateTime, default=datetime.datetime.now)
    updated = Column(types.DateTime, default=datetime.datetime.now)

    __table_args__ = (UniqueConstraint('package_id', 'user_id', name='uq_package_id_user_id'),)

    def __init__(self, package_id: str, rating: int, rater_ip: str, user_id: str = None):
        self.package_id = package_id
        self.rating = rating
        self.rater_ip = rater_ip
        self.user_id = user_id

    def as_dict(self):
        context = {'model': model}
        rating_dict = dictization.table_dictize(self, context)
        return rating_dict

    @classmethod
    def create(cls, package_id: str, rating: int, rater_ip: str, user_id: str = None) -> None:

        rating = round(rating, 2)
        user_rating = cls.get_user_rating(package_id, user_id, rater_ip)

        if user_rating is not None:
            cls._update_review(user_rating, rating)
        else:
            cls._create_review(
                package_id=package_id,
                rating=rating,
                user_id=user_id,
                rater_ip=rater_ip
            )

    @classmethod
    def _create_review(cls, package_id: str, rating: int, user_id: str = None, rater_ip: str = None) -> None:
        if not user_id and not rater_ip:
            raise ValueError('User ID or IP address must be provided')
        new_rating = Rating(
            package_id=package_id,
            rating=rating,
            user_id=user_id,
            rater_ip=rater_ip
        )
        new_rating.save()

        log.info('Review added for package')

    @classmethod
    def _update_review(cls, existing_rating, rating):
        existing_rating.rating = rating
        existing_rating.save()
        log.info('Review updated for package')

    @classmethod
    def get_rating(cls, package_id: str) -> Optional[dict]:
        ratings = model.Session.query(cls) \
            .filter(cls.package_id == package_id) \
            .all()

        average = sum(r.rating for r in ratings) / float(len(ratings)) if (
                len(ratings) > 0) else 0
        return {
            'rating': round(average, 2),
            'ratings_count': len(ratings)
        }

    @classmethod
    def get_ratings_for_packages(cls, package_ids: list) -> dict:
        """Get ratings for multiple packages in a single query.

        Returns a dict mapping package_id to {'rating': float, 'ratings_count': int}
        """
        from sqlalchemy import func

        if not package_ids:
            return {}

        results = model.Session.query(
            cls.package_id,
            func.avg(cls.rating).label('avg_rating'),
            func.count(cls.id).label('count')
        ).filter(
            cls.package_id.in_(package_ids)
        ).group_by(cls.package_id).all()

        ratings_map = {
            row.package_id: {
                'rating': round(float(row.avg_rating), 2),
                'ratings_count': row.count
            }
            for row in results
        }

        # Fill in packages with no ratings
        for package_id in package_ids:
            if package_id not in ratings_map:
                ratings_map[package_id] = {'rating': 0, 'ratings_count': 0}

        return ratings_map

    @classmethod
    def _exists_user(cls, user_id: str) -> bool:
        return model.Session.query(User).filter(User.id == user_id).first() is not None

    @classmethod
    def get_user_rating(cls, package_id: str, user_id: str, rater_ip: str) -> Optional['Rating']:

        rating = None
        if cls._exists_user(user_id):
            rating = model.Session.query(cls).filter(
                cls.package_id == package_id,
                cls.user_id == user_id).first()
        else:
            rating = model.Session.query(cls).filter(
                cls.package_id == package_id,
                cls.rater_ip == rater_ip).first()

        return rating

# def init_tables(engine):
#     Base.metadata.create_all(engine)
#     log.info('Rating database tables are set-up')
