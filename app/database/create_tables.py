from app.database.database import Base, engine

# Import all models so SQLAlchemy knows about them
from app.models.user import User


def create_tables():
    Base.metadata.create_all(bind=engine)
    print(" All database tables created successfully!")


if __name__ == "__main__":
    create_tables()