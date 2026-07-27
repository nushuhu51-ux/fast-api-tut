from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth import models, schemas, utils
from auth.auth_database import get_db
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

SECRET_KEY = "7uKYC1hSn79JkU_vBPrFKkzRouUFIpz4ipvHpiVYrvY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()


# ----------------------------
# Create JWT Token
# ----------------------------
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ----------------------------
# User Registration
# ----------------------------
@app.post("/signup")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = (
        db.query(models.User)
        .filter(models.User.username == user.username)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    hashed_password = utils.hash_password(user.password)

    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role
    }


# ----------------------------
# Login
# ----------------------------
@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = (
        db.query(models.User)
        .filter(models.User.username == form_data.username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username"
        )

    if not utils.verify_password(
        form_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )

    access_token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ----------------------------
# OAuth2 Scheme
# ----------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# ----------------------------
# Get Current User
# ----------------------------
def get_current_user(token: str = Depends(oauth2_scheme)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username: str = payload.get("sub")
        role: str = payload.get("role")

        if username is None or role is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    return {
        "username": username,
        "role": role
    }


# ----------------------------
# Protected Route
# ----------------------------
@app.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {
        "Message": f"Hello, {current_user['username']} | You accessed a protected route"
    }


# ----------------------------
# Role Authorization
# ----------------------------
def require_roles(allowed_roles: list[str]):
    def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")

        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

        return current_user

    return role_checker


# ----------------------------
# Profile
# ----------------------------
@app.get("/profile")
def profile(
    current_user: dict = Depends(
        require_roles(["user", "admin"])
    )
):
    return {
        "Message": f"Profile of {current_user['username']} ({current_user['role']})"
    }


# ----------------------------
# User Dashboard
# ----------------------------
@app.get("/user/dashboard")
def user_dashboard(
    current_user: dict = Depends(require_roles(["user"]))
):
    return {
        "Message": "Welcome User"
    }


# ----------------------------
# Admin Dashboard
# ----------------------------
@app.get("/admin/dashboard")
def admin_dashboard(
    current_user: dict = Depends(require_roles(["admin"]))
):
    return {
        "Message": "Welcome Admin"
    }