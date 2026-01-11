from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
import hashlib

app = FastAPI(title="Simple Login API")

# In-memory user database
users_db = {
    "user@example.com": {
        "email": "user@example.com",
        "password_hash": hashlib.sha256("password123".encode()).hexdigest(),
        "name": "John Doe"
    }
}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str
    user: Optional[dict] = None


@app.get("/")
def read_root():
    return {"message": "Welcome to Login API", "endpoints": ["/login"]}


@app.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest):
    email = credentials.email
    password = credentials.password
    
    # Check if user exists
    if email not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if users_db[email]["password_hash"] != password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Successful login
    user_data = {
        "email": users_db[email]["email"],
        "name": users_db[email]["name"]
    }
    
    return LoginResponse(
        success=True,
        message="Login successful",
        user=user_data
    )


# Test cases
def test_successful_login():
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    response = client.post("/login", json={
        "email": "user@example.com",
        "password": "password123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Login successful"
    assert data["user"]["email"] == "user@example.com"
    print("Test 1 passed: Successful login")


def test_failed_login_invalid_password():
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    response = client.post("/login", json={
        "email": "user@example.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid email or password"
    print("Test 2 passed: Failed login with invalid password")


if __name__ == "__main__":
    # Run tests
    print("Running tests...")
    test_successful_login()
    test_failed_login_invalid_password()
    print("\nAll tests passed!")
    
    print("\nTo run the server:")
    print("uvicorn example:app --reload")