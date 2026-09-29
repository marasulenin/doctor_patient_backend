
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db


# =========================================================
# TEST DATABASE
# =========================================================

TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },
    poolclass=StaticPool
)


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


# =========================================================
# CREATE TEST DATABASE TABLES
# =========================================================

Base.metadata.create_all(
    bind=test_engine
)


# =========================================================
# TEST DATABASE DEPENDENCY
# =========================================================

def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db

    finally:
        db.close()


# =========================================================
# OVERRIDE FASTAPI DATABASE DEPENDENCY
# =========================================================

app.dependency_overrides[get_db] = override_get_db


# =========================================================
# CLEAN TEST DATABASE AFTER TEST SESSION
# =========================================================

def pytest_sessionfinish(session, exitstatus):
    Base.metadata.drop_all(
        bind=test_engine
    )

