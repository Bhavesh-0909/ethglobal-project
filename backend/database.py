from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Replace with your Supabase connection string
DATABASE_URL = "postgresql://postgres:ethglobal@db.epvzendwbxqcauosxnuj.supabase.co:5432/postgres"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# Session local class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()