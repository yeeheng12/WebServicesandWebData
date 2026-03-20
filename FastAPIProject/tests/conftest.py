import os
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

# Set test DB before importing app modules that depend on DATABASE_URL
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"

from app.main import app
from app.database import Base, get_db
from app import models
from app.security import get_password_hash

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        try:
            session.close()
        finally:
            if transaction.is_active:
                transaction.rollback()
            if not connection.closed:
                connection.close()

@pytest.fixture()
def client(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def viewer_user(db_session):
    user = models.User(
        username="viewer1",
        email="viewer@test.com",
        hashed_password=get_password_hash("Password123"),
        role="viewer",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def editor_user(db_session):
    user = models.User(
        username="editor1",
        email="editor@test.com",
        hashed_password=get_password_hash("Password123"),
        role="editor",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def admin_user(db_session):
    user = models.User(
        username="admin1",
        email="admin@test.com",
        hashed_password=get_password_hash("Password123"),
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def login_and_get_token(client, username, password):
    response = client.post(
        "/auth/login",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture()
def viewer_token(client, viewer_user):
    return login_and_get_token(client, "viewer1", "Password123")


@pytest.fixture()
def editor_token(client, editor_user):
    return login_and_get_token(client, "editor1", "Password123")


@pytest.fixture()
def admin_token(client, admin_user):
    return login_and_get_token(client, "admin1", "Password123")


@pytest.fixture()
def viewer_headers(viewer_token):
    return {"Authorization": f"Bearer {viewer_token}"}


@pytest.fixture()
def editor_headers(editor_token):
    return {"Authorization": f"Bearer {editor_token}"}


@pytest.fixture()
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture()
def sample_property(db_session, editor_user):
    prop = models.PropertyRecord(
        transaction_id="txn-001",
        price=250000.0,
        sale_date=date(2024, 1, 10),
        postcode="LS1 1AA",
        property_type="F",
        town_city="Leeds",
        district="Leeds",
        county="West Yorkshire",
        current_energy_rating="C",
        current_energy_efficiency=72.0,
        total_floor_area=80.0,
        created_by_user_id=editor_user.id,
        updated_by_user_id=editor_user.id,
    )
    db_session.add(prop)
    db_session.commit()
    db_session.refresh(prop)
    return prop


@pytest.fixture()
def sample_certificate(db_session, sample_property, editor_user):
    cert = models.EnergyCertificate(
        property_id=sample_property.id,
        lmk_key="LMK-001",
        current_energy_rating="C",
        potential_energy_rating="B",
        current_energy_efficiency=72.0,
        potential_energy_efficiency=82.0,
        total_floor_area=80.0,
        created_by_user_id=editor_user.id,
        updated_by_user_id=editor_user.id,
    )
    db_session.add(cert)
    db_session.commit()
    db_session.refresh(cert)
    return cert


@pytest.fixture()
def property_payload():
    return {
        "transaction_id": "txn-create-001",
        "price": 275000.0,
        "sale_date": "2024-04-10",
        "postcode": "LS2 8AA",
        "property_type": "F",
        "town_city": "Leeds",
        "district": "Leeds",
        "county": "West Yorkshire",
        "current_energy_rating": "B",
        "potential_energy_rating": "A",
        "current_energy_efficiency": 81.0,
        "potential_energy_efficiency": 90.0,
        "total_floor_area": 85.0,
    }


@pytest.fixture()
def certificate_payload(sample_property):
    return {
        "property_id": sample_property.id,
        "lmk_key": "LMK-CREATE-001",
        "current_energy_rating": "C",
        "potential_energy_rating": "B",
        "current_energy_efficiency": 72.0,
        "potential_energy_efficiency": 80.0,
        "total_floor_area": 80.0,
    }


@pytest.fixture()
def analytics_properties(db_session, editor_user):
    properties = [
        models.PropertyRecord(
            transaction_id="txn-101",
            price=250000.0,
            sale_date=date(2024, 1, 10),
            postcode="LS1 1AA",
            property_type="F",
            town_city="Leeds",
            district="Leeds",
            county="West Yorkshire",
            current_energy_rating="C",
            potential_energy_rating="B",
            current_energy_efficiency=72.0,
            potential_energy_efficiency=80.0,
            total_floor_area=80.0,
            created_by_user_id=editor_user.id,
            updated_by_user_id=editor_user.id,
        ),
        models.PropertyRecord(
            transaction_id="txn-102",
            price=300000.0,
            sale_date=date(2024, 2, 15),
            postcode="LS2 2BB",
            property_type="T",
            town_city="Leeds",
            district="Leeds",
            county="West Yorkshire",
            current_energy_rating="B",
            potential_energy_rating="A",
            current_energy_efficiency=82.0,
            potential_energy_efficiency=90.0,
            total_floor_area=95.0,
            created_by_user_id=editor_user.id,
            updated_by_user_id=editor_user.id,
        ),
        models.PropertyRecord(
            transaction_id="txn-103",
            price=180000.0,
            sale_date=date(2023, 11, 1),
            postcode="M1 1CC",
            property_type="F",
            town_city="Manchester",
            district="Manchester",
            county="Greater Manchester",
            current_energy_rating="F",
            potential_energy_rating="D",
            current_energy_efficiency=45.0,
            potential_energy_efficiency=60.0,
            total_floor_area=70.0,
            created_by_user_id=editor_user.id,
            updated_by_user_id=editor_user.id,
        ),
        models.PropertyRecord(
            transaction_id="txn-104",
            price=420000.0,
            sale_date=date(2024, 3, 20),
            postcode="BS1 4DD",
            property_type="D",
            town_city="Bristol",
            district="Bristol",
            county="Bristol",
            current_energy_rating="A",
            potential_energy_rating="A",
            current_energy_efficiency=92.0,
            potential_energy_efficiency=95.0,
            total_floor_area=120.0,
            created_by_user_id=editor_user.id,
            updated_by_user_id=editor_user.id,
        ),
        models.PropertyRecord(
            transaction_id="txn-105",
            price=210000.0,
            sale_date=date(2024, 1, 25),
            postcode="LS3 3EE",
            property_type="F",
            town_city="Leeds",
            district="Leeds",
            county="West Yorkshire",
            current_energy_rating="E",
            potential_energy_rating="C",
            current_energy_efficiency=55.0,
            potential_energy_efficiency=74.0,
            total_floor_area=76.0,
            created_by_user_id=editor_user.id,
            updated_by_user_id=editor_user.id,
        ),
    ]

    db_session.add_all(properties)
    db_session.commit()

    for p in properties:
        db_session.refresh(p)

    return properties