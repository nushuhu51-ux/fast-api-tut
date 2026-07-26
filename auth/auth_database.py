from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# MySQL Configuration
DB_USERNAME = "root"
DB_PASSWORD = "sami2539E"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "fastapi_db"


DATABASE_URL = (
    f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


engine = create_engine(DATABASE_URL)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()


# Database dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()