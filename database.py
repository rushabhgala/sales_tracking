from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///menu_tracker.db"

#the engine manages connection to the database
engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)

#session local is a factory for database sessions
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

#Base is the base class for all our models
Base = declarative_base()