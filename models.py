from sqlalchemy import Column, Integer, String, Boolean, ForeignKey,\
    create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)
    active = Column(Boolean, default=False)
    activation = relationship("Activation",
                              uselist=False,
                              back_populates="user")

    def __repr__(self):
        return "<User: %s>" % self.email

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def is_valid_password(self, password):
        return check_password_hash(self.password, password)

    @property
    def is_active(self):
        return self.active

    @property
    def is_authenticated(self):
        return self.active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class Activation(Base):
    __tablename__ = 'activations'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="activation")
    code = Column(String, unique=True)
