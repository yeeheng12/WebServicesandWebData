from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, schemas
from app.dependencies import get_db
from app.security import authenticate_user, create_access_token, get_current_user, require_admin

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register user",
    description="Creates a new user account.",
)
def register_user(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    safe_user_data = schemas.UserCreate(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        role="viewer",
    )

    user, error = crud.create_user(db=db, user_data=safe_user_data)

    if error == "duplicate_username":
        raise HTTPException(status_code=409, detail="username already exists")
    if error == "duplicate_email":
        raise HTTPException(status_code=409, detail="email already exists")

    return user


@router.post(
    "/login",
    response_model=schemas.LoginResponse,
    summary="Login user",
    description="Authenticates a user and returns a JWT bearer token.",
)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }


@router.get(
    "/me",
    response_model=schemas.UserResponse,
    summary="Current user",
    description="Returns the currently authenticated user.",
)
def read_current_user(current_user = Depends(get_current_user)):
    return current_user