from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
from models import Base

def init_db(db_name=None):
    """
    Initialize database and models
    :param db_name: Database name for SQLite
    :return: Engine object
    """
    engine = create_engine('sqlite:///%s' % (db_name or config.DATABASE))
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    return engine

def get_session():
    """
    Create session after initializing database. This method can be optimized
    in order to not to call model creation all the time
    :return: Database Session
    """
    engine = init_db()
    DBSession = sessionmaker(bind=engine)
    return DBSession()
