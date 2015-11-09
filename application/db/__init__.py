# flake8:noqa
from application.db.db import *
from application.db import init


class AlembicVersion(db.Model):
    __tablename__ = 'alembic_version'

    version_num = db.Column(db.String(), primary_key=True)
