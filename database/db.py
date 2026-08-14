from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import DATABASE_URL


# ============================================================
# Database Engine
# ============================================================
# ============================================================
# Database Engine
# ============================================================

if DATABASE_URL.startswith("sqlite"):

    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "check_same_thread": False
        }
    )

else:

    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_timeout=30,
        connect_args={
            "connect_timeout": 10,
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5,
        }
    )


# ============================================================
# Session
# ============================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ============================================================
# Base Model
# ============================================================

Base = declarative_base()