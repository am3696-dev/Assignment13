import pytest
from playwright.sync_api import Page, expect
import uuid

# --- Helper Function ---
def get_unique_user():
    """
    Generates unique user data using UUID to guarantee no collisions.
    """
    # UUID4 generates a random 32-character string
    unique_id = str(uuid.uuid4())[:8] 
    return {
        "first_name": "Test",
        "last_name": "User",
        "username": f"user_{unique_id}",
        "email": f"test_{unique_id}@example.com",
        # Strict password compliance
        "password": "SecurePass123!", 
        "confirm_password": "SecurePass123!"
    }

# --- Tests ---

def test_register_flow_success(page: Page):
    """
    Test that a user can register with valid data.
    """
    user_data = get_unique_user()
    
    # 1. Navigate to Register Page
    page.goto("http://localhost:8000/register") 
    
    # 2. Fill Form Data
    page.fill("#first_name", user_data["first_name"])
    page.fill("#last_name", user_data["last_name"])
    page.fill("#username", user_data["username"])
    page.fill("#email", user_data["email"])
    page.fill("#password", user_data["password"])
    page.fill("#confirm_password", user_data["confirm_password"])
    
    # 3. Submit
    page.click("button[type='submit']")
    
    # 4. Verify Success Message matches your JS
    expect(page.locator("#successMessage")).to_contain_text("Registration successful")

def test_register_password_mismatch(page: Page):
    """
    Test that the frontend catches mismatched passwords.
    """
    page.goto("http://localhost:8000/register")
    
    page.fill("#first_name", "Bad")
    page.fill("#last_name", "Pass")
    page.fill("#username", "badpassuser")
    page.fill("#email", "badpass@example.com")
    page.fill("#password", "SecurePass123!")
    page.fill("#confirm_password", "DifferentPass123!") 
    
    page.click("button[type='submit']")
    
    # Expect error message
    expect(page.locator("#errorMessage")).to_contain_text("Passwords do not match")

def test_login_flow_success(page: Page):
    """
    Test that a registered user can log in.
    """
    # 1. Register a user first (Using the UI to ensure full flow works)
    user_data = get_unique_user()
    page.goto("http://localhost:8000/register")
    page.fill("#first_name", user_data["first_name"])
    page.fill("#last_name", user_data["last_name"])
    page.fill("#username", user_data["username"])
    page.fill("#email", user_data["email"])
    page.fill("#password", user_data["password"])
    page.fill("#confirm_password", user_data["confirm_password"])
    page.click("button[type='submit']")
    
    # Wait for success to ensure user is created before trying to login
    expect(page.locator("#successMessage")).to_contain_text("Registration successful")
    
    # 2. Navigate to Login
    page.goto("http://localhost:8000/login")
    
    # 3. Fill Login Form
    page.fill("#username", user_data["username"])
    page.fill("#password", user_data["password"])
    page.click("button[type='submit']")
    
    # 4. Verify Success
    expect(page.locator("#successMessage")).to_contain_text("Login successful")

def test_login_failure(page: Page):
    """
    Test invalid credentials.
    """
    page.goto("http://localhost:8000/login")
    
    page.fill("#username", "nonexistentuser")
    page.fill("#password", "WrongPass123!")
    page.click("button[type='submit']")
    
    # We updated this to match your actual API response
    expect(page.locator("#errorMessage")).to_contain_text("Invalid username or password")