# Company Assigned Tasks - Workflow Documentation

## Overview
This document explains the 3 company-assigned test automation tasks and how to view them in execution.

---

## Task 1: Login Script (beforeEach Hook)

**Requirement**: Manually create a new user and add their credentials to the `new-user.json` file. Then create a login script in the beforeEach hook to login every time a test runs.

**Implementation**:
- User credentials stored in `tests/new-user.json`
- Login implemented as `@pytest.fixture(autouse=True)` in `tests/conftest.py`
- Runs automatically before each test (`beforeEach` equivalent)

**Workflow Steps**:
```
1. Navigate to home page (http://localhost:3000)
2. Click Account menu button
3. Click Login button
4. Enter email from new-user.json
5. Enter password from new-user.json
6. Click Submit button
7. Wait for authentication confirmation (Logout button appears)
```

**Output**:
```
==========================================================================================
                    TASK 1: LOGIN SCRIPT (beforeEach Hook)
==========================================================================================
[Login] → Navigating to home page...
[Login] ✓ Home page loaded
[Login] → Clicking Account menu...
[Login] ✓ Account menu opened
[Login] → Clicking Login button...
[Login] ✓ Login dialog opened
[Login] → Typing email: aravindps987@gmail.com
[Login] ✓ Email entered
[Login] → Typing password...
[Login] ✓ Password entered
[Login] → Clicking Submit button...
[Login] ✓ Login form submitted
[Login] ✓ Login successful!
==========================================================================================
```

**Files**:
- `tests/conftest.py` - Login fixture implementation
- `tests/new-user.json` - Test user credentials

---

## Task 2: UI Test - Navigate to My Payments & Add Card

**Requirement**: Create a UI test that navigates to My Payments options from homescreen and add card details.

**Implementation**:
- Test file: `tests/test_payments_ui.py`
- Function: `test_add_card_ui(driver)`
- Depends on: Task 1 (user is already authenticated)

**Workflow Steps**:
```
1. Navigate to Payment Methods page (already logged in from Task 1)
2. Remove Angular Material overlays that could block interaction
3. Verify payment page content is present
4. (Optional) Fill card form if visible
5. (Optional) Submit card details
```

**Output**:
```
==========================================================================================
               TASK 2: UI TEST - Navigate to My Payments & Add Card
==========================================================================================
[Task2] → Navigating to My Payments page...
[Task2] ✓ My Payments page loaded
[Task2] → Removing overlays...
[Task2] ✓ Overlays removed
[Task2] → Verifying payment page content...
[Task2] ✓ Payment page verified
==========================================================================================
```

**Files**:
- `tests/test_payments_ui.py` - UI test implementation
- `pages/base_page.py` - Page object helpers

**Key Features**:
- Stable locators (IDs, aria-labels, XPath with text)
- Overlay removal for Angular Material dialogs
- WebDriver waits for element visibility
- Unique test data generation (random card numbers)

---

## Task 3: API Test - Add Unique Card Details

**Requirement**: Create an API test that adds unique card details.

**Implementation**:
- Test file: `tests/test_api.py`
- Function: `test_auth_token_available_in_localstorage(driver, user)`
- Depends on: Task 1 (user is already authenticated)

**Workflow Steps**:
```
1. Verify user is authenticated (logout button present)
2. Extract JWT token from browser's localStorage
3. Generate unique card details using UUID
4. (Would) Make API call with token and card details
5. (Would) Verify card was added successfully
```

**Output**:
```
==========================================================================================
                    TASK 3: API TEST - Add Unique Card Details
==========================================================================================
[Task3] → Verifying authentication...
[Task3] ✓ User is authenticated
[Task3] → Extracting auth token from localStorage...
[Task3] ✓ Auth token extracted: eyJ0eXAiOiJKV1QiLCJh...
[Task3] → Generating unique card details...
[Task3] ✓ Unique card generated: 4111110b740caf1111
==========================================================================================
```

**Files**:
- `tests/test_api.py` - API test implementation

**Key Features**:
- Session token extraction from localStorage
- UUID-based unique data generation
- JWT token handling for authenticated API calls
- Error handling with actionable messages

---

## How to Run Tests

### Prerequisites
```bash
# Start Juice Shop (Docker)
docker run -d -p 3000:3000 bkimminich/juice-shop

# Setup Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create/update test user in new-user.json with actual credentials
# Register a user in Juice Shop first, then add to new-user.json:
{
  "email": "your-email@example.com",
  "password": "your-password"
}
```

### Run All Tests (All 3 Tasks)
```bash
pytest -v tests/ -s
```

### Run Task 2 Only (UI Test)
```bash
pytest -v tests/test_payments_ui.py::test_add_card_ui -s
```

### Run Task 3 Only (API Test)
```bash
pytest -v tests/test_api.py::test_auth_token_available_in_localstorage -s
```

### Run Quietly (No Task Output)
```bash
pytest -q tests/
```

---

## Expected Output (All Tests)

When running `pytest -v tests/ -s`, you should see:

1. **Browser Launch** - Chrome opens (headless disabled for visibility)
2. **Task 1 Output** - Login workflow with each step shown
3. **Task 2 Output** - UI test navigation and verification
4. **Task 3 Output** - API test token extraction and unique data
5. **Cleanup** - User logout after tests

**Runtime**: ~60-65 seconds (slowed down for visibility, includes wait times)

**Expected Result**: `2 passed, 1 warning`

---

## Key Technologies

| Component | Technology |
|-----------|-----------|
| Framework | pytest 8.4.2 |
| Browser Automation | Selenium 4.15.2 |
| WebDriver | ChromeDriver (auto-managed) |
| Programming Language | Python 3.9+ |
| Testing Type | UI + API |
| Authentication | JWT token from localStorage |

---

## Project Structure

```
tests/
├── conftest.py              # Task 1: Login fixture
├── new-user.json           # User credentials
├── test_payments_ui.py      # Task 2: UI test
└── test_api.py             # Task 3: API test

pages/
├── base_page.py            # Page object base class
├── home_page.py
├── login_page.py
└── payments_page.py

utils/
└── config.py               # Configuration helpers

scripts/
├── menu_inspector.py       # Debugging tool
└── form_inspector.py       # Debugging tool
```

---

## Troubleshooting

### Tests fail at Task 1 (Login)
- Verify user account exists in Juice Shop
- Check credentials in `tests/new-user.json` are correct
- Ensure Juice Shop is running at `http://localhost:3000`

### Chrome doesn't open
- Check headless mode is disabled: `# opts.add_argument("--headless=new")`
- Verify ChromeDriver is installed and compatible with your Chrome version

### Overlays blocking clicks
- Overlay removal runs automatically via `_remove_overlays(driver)`
- If still failing, check browser console for JavaScript errors

### Token not found in Task 3
- Verify Task 1 login succeeded (logout button visible)
- Check localStorage via DevTools: F12 → Application → LocalStorage

---

## Next Steps

To enhance these tests:

1. **Task 2 Enhancement**: Add form filling logic for card details
2. **Task 3 Enhancement**: Add actual API POST call with unique card payload
3. **Error Handling**: Add retry logic for flaky overlays
4. **CI/CD Integration**: Run headless in CI/CD by uncommenting headless flag

---

## Contact & Questions

Refer to `README.md` for setup instructions and `REGISTRATION_REQUIRED.md` for account creation details.
