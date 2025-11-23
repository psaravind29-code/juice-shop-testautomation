# Juice Shop Test Automation — Setup & Running Guide

This project contains **pytest-based UI and API tests** written in Python using Selenium for OWASP Juice Shop.

## Prerequisites

### 1. Docker
Install Docker from [docker.com](https://www.docker.com/). Verify installation:
```bash
docker --version
```

### 2. Python 3.9+
Ensure Python is installed. Verify:
```bash
python3 --version
```

### 3. Python Virtual Environment
Create a virtual environment (recommended):
```bash
python3 -m venv .venv
source .venv/bin/activate   # On macOS/Linux
# or
.venv\Scripts\activate       # On Windows
```

## Setup Steps

### Step 1: Start Juice Shop in Docker

```bash
docker run -d -p 3000:3000 bkimminich/juice-shop
```

Verify the app is running:
- Open http://localhost:3000 in your browser
- You should see the Juice Shop homepage

### Step 2: Create a Test User in Juice Shop

1. On the Juice Shop homepage, click **Account** (top-right) → **Login**
2. Click **Create Account**
3. Fill in:
   - **Email:** `aravindps987@gmail.com`
   - **Password:** `cat@123`
   - **Security Question:** (any answer)
4. Click **Register** and verify success

### Step 3: Install Dependencies

From the project root:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Verify ChromeDriver is downloaded:
```bash
python -c "from webdriver_manager.chrome import ChromeDriverManager; print(ChromeDriverManager().install())"
```

### Step 4: Verify Test User Credentials

Check `tests/new-user.json`:
```json
{
  "email": "aravindps987@gmail.com",
  "password": "cat@123"
}
```

**Important:** This must match a manually registered user in Juice Shop (from Step 2).

## Running Tests

### Run All Tests
```bash
pytest -q
```

### Run a Single Test
```bash
# UI test only
pytest -q tests/test_payments_ui.py::test_add_card_ui

# API test only
pytest -q tests/test_api.py::test_add_card_api_using_token_from_localstorage
```

### Run with Verbose Output
```bash
pytest -v tests/
```

### View Browser (Debug Mode)

Edit `tests/conftest.py` and comment out or remove this line:
```python
opts.add_argument("--headless=new")
```

Then run tests — Chrome will open and you can watch the automation.

## Test Structure

### `tests/conftest.py` (Fixtures)
- **`driver`** — Selenium WebDriver instance (session scope)
- **`user`** — Test account credentials from `new-user.json` (session scope)
- **`ensure_user_registered`** — Registration helper (session scope, autouse)
- **`login`** — Auto-login before each test (function scope, autouse)

### `tests/test_payments_ui.py` (UI Tests)
- **`test_add_card_ui`** — Navigate to Payments and add a card via the UI
  - Demonstrates stable locators (IDs, XPath with text)
  - Handles overlays and dynamic elements
  - Generates unique card numbers for each run

### `tests/test_api.py` (API Tests)
- **`test_add_card_api_using_token_from_localstorage`** — Add a card via the API
  - Extracts auth token from browser localStorage
  - Makes authenticated POST to `/api/PaymentMethods`
  - Verifies response status code

### `pages/` (Page Objects)
Base classes for UI interactions; not currently used but available for refactoring.

## Locator Strategy

Tests use **stable locators** to minimize flakiness:
- **IDs** — Most stable (e.g., `#navbarAccount`, `#loginButton`)
- **aria-label** — Accessible labels (e.g., `[aria-label="Show/hide account menu"]`)
- **XPath with text()** — For dynamic or variable text (e.g., `//*[contains(text(),'Payment Methods')]`)
- **CSS class selectors** — With caution for dynamic classes

**Avoid:**
- Generic XPath indices (e.g., `//button[5]`)
- Deep CSS selectors that depend on DOM depth
- Hard-coded delays (use WebDriverWait instead)

## Handling Overlays

Tests include defensive overlay removal and JS click fallbacks:
```python
def _remove_overlays(driver):
    """Remove CDK overlays, dialogs, and click close buttons."""
    driver.execute_script("""
    const selectors = ['.cdk-overlay-backdrop', '.mat-mdc-dialog-surface', ...];
    selectors.forEach(s => { 
        document.querySelectorAll(s).forEach(n => n.remove()); 
    });
    """)

def _click_with_fallback(driver, element):
    """Click with JS fallback if normal click fails."""
    try:
        element.click()
    except:
        driver.execute_script("arguments[0].click();", element)
```

## Troubleshooting

### Test Fails: "Element Click Intercepted"
- Overlays may be covering buttons
- Check `_remove_overlays()` is called before sensitive clicks
- Verify Juice Shop hasn't changed DOM structure (use browser DevTools)

### Test Fails: "TimeoutException"
- Verify test user account exists in Juice Shop (Step 2)
- Check credentials in `new-user.json` match registered account
- Increase wait time if network is slow (edit `WebDriverWait(driver, 15)`)

### ChromeDriver Issues on macOS M1
- Run with `--platform linux/amd64`:
  ```bash
  docker run -d --platform linux/amd64 -p 3000:3000 bkimminich/juice-shop
  ```

### Tests Pass Locally But Fail in CI/CD
- Ensure Docker Juice Shop is running and accessible
- Verify test user account is created (or implement dynamic registration)
- Check headless browser compatibility (use `--headless=new`)

## Clean Code Practices Applied

✓ **Descriptive variable names** — `acct_btn`, `pm_link`, `card_number`  
✓ **Helper functions** — `_remove_overlays()`, `_click_with_fallback()`, `_extract_auth_token()`  
✓ **Stable locators** — IDs, aria-labels, XPath with text  
✓ **Modularity** — Each test is independent; fixtures handle setup  
✓ **Error handling** — Try/except with fallbacks instead of hard waits  
✓ **Comments** — Docstrings for tests and helper functions  

## References

- [Selenium Documentation](https://selenium.dev/documentation/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [OWASP Juice Shop](https://github.com/bkimminich/juice-shop)
- [WebDriver Wait Patterns](https://selenium.dev/documentation/webdriver/waits/)
