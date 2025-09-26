from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Example: postgresql://username:password@localhost:5432/mydb
DATABASE_URL = "postgresql://postgres:password@localhost:5432/mydb"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()