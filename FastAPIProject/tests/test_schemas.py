import pytest
from pydantic import ValidationError

from app.schemas import (
    UserCreate,
    PropertyCreate,
    PropertyUpdate,
    EnergyCertificateCreate,
    EnergyCertificateUpdate,
)


def test_user_create_valid():
    user = UserCreate(
        username="validuser",
        email="valid@test.com",
        password="Password123",
        role="viewer",
    )
    assert user.username == "validuser"
    assert user.role == "viewer"


def test_user_create_invalid_role_raises_validation_error():
    with pytest.raises(ValidationError):
        UserCreate(
            username="validuser",
            email="valid@test.com",
            password="Password123",
            role="superadmin",
        )


def test_property_create_invalid_energy_rating_raises_validation_error():
    with pytest.raises(ValidationError):
        PropertyCreate(
            price=250000.0,
            current_energy_rating="Z",
        )


def test_property_create_invalid_efficiency_above_100_raises_validation_error():
    with pytest.raises(ValidationError):
        PropertyCreate(
            price=250000.0,
            current_energy_efficiency=120.0,
        )


def test_property_create_negative_floor_area_raises_validation_error():
    with pytest.raises(ValidationError):
        PropertyCreate(
            price=250000.0,
            total_floor_area=-5.0,
        )


def test_property_create_price_must_be_positive():
    with pytest.raises(ValidationError):
        PropertyCreate(
            price=0,
        )


def test_property_update_allows_partial_fields():
    update = PropertyUpdate(price=123456.0)
    assert update.price == 123456.0
    assert update.transaction_id is None


def test_energy_certificate_create_invalid_rating_raises_validation_error():
    with pytest.raises(ValidationError):
        EnergyCertificateCreate(
            property_id=1,
            current_energy_rating="X",
        )


def test_energy_certificate_create_invalid_efficiency_raises_validation_error():
    with pytest.raises(ValidationError):
        EnergyCertificateCreate(
            property_id=1,
            current_energy_efficiency=-1,
        )


def test_energy_certificate_update_negative_floor_area_raises_validation_error():
    with pytest.raises(ValidationError):
        EnergyCertificateUpdate(
            total_floor_area=-2,
        )

def test_user_create_username_too_short_raises_validation_error():
    with pytest.raises(ValidationError):
        UserCreate(
            username="ab",
            email="valid@test.com",
            password="Password123",
            role="viewer",
        )


def test_user_create_username_too_long_raises_validation_error():
    with pytest.raises(ValidationError):
        UserCreate(
            username="a" * 51,
            email="valid@test.com",
            password="Password123",
            role="viewer",
        )


def test_user_create_password_min_boundary_valid():
    user = UserCreate(
        username="validuser",
        email="valid@test.com",
        password="12345678",
        role="viewer",
    )
    assert user.password == "12345678"


def test_user_create_password_below_min_raises_validation_error():
    with pytest.raises(ValidationError):
        UserCreate(
            username="validuser",
            email="valid@test.com",
            password="1234567",
            role="viewer",
        )


def test_user_create_default_role_is_viewer():
    user = UserCreate(
        username="validuser",
        email="valid@test.com",
        password="Password123",
    )
    assert user.role == "viewer"