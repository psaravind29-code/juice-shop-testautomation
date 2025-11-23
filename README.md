# Juice Shop Test Automation

Comprehensive pytest-based test suite for **OWASP Juice Shop** using Selenium WebDriver. Implements UI and API testing with stable locators, page object model pattern, and production-ready practices.

**Repository**: https://github.com/psaravind29-code/juice-shop-testautomation

---

## 📋 Task Overview

This project fulfills three core automation tasks:

| Task | Description | Implementation |
|------|-------------|-----------------|
| **Task 1** | Automatic login (beforeEach hook equivalent) | `tests/conftest.py` – `login` autouse fixture |
| **Task 2** | UI test: Navigate to Payments, add card | `tests/test_payments_ui.py` – Full flow with assertions |
| **Task 3** | API test: Add unique card via authenticated endpoint | `tests/test_api.py` – Token extraction + POST request |

---

## 🚀 Quick Start

### Prerequisites
- **Docker & Docker Desktop** installed and running
- **Python 3.9+** (tested on 3.9.6)
- **Juice Shop running** on `http://localhost:3000`

### 1. Start Juice Shop (5 seconds)
```bash
docker run -d -p 3000:3000 bkimminich/juice-shop
```

### 2. Clone & Setup (30 seconds)
```bash
git clone https://github.com/psaravind29-code/juice-shop-testautomation.git
cd juice-shop-testautomation

python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Register Test User (5 seconds) ⚠️ **CRITICAL**
Open http://localhost:3000 in browser and manually create account:
- **Email:** `aravindps987@gmail.com`
- **Password:** `cat@123`
- **Security Question:** Any answer (e.g., "What's your favorite color?" → "blue")

See `REGISTRATION_REQUIRED.md` for detailed screenshots/steps.

### 4. Run Tests (60 seconds)
```bash
# All tests
pytest -v

# Single test
pytest -v tests/test_payments_ui.py::test_add_card_ui

# With output
pytest -v -s tests/test_payments_ui.py

# API test only
pytest -v tests/test_api.py::test_add_card_api_using_token_from_localstorage
```

---

## 📁 Project Structure

```
juice-shop-testautomation/
├── README.md                          # This file
├── SETUP.md                           # Detailed setup guide
├── TESTING_GUIDE.md                   # Testing & troubleshooting
├── REGISTRATION_REQUIRED.md           # Account registration steps
├── requirements.txt                   # Python dependencies (pinned versions)
│
├── pages/                             # Page Object Model (POM)
│   ├── base_page.py                   # BasePage with waits, logging
│   ├── home_page.py                   # Navigation to payments
│   ├── login_page.py                  # Login actions (if needed)
│   └── payments_page.py               # Card addition form handling
│
├── tests/                             # Test files & fixtures
│   ├── conftest.py                    # Pytest fixtures (driver, login autouse)
│   ├── new-user.json                  # Test user credentials
│   ├── test_payments_ui.py            # UI test: Add card via payments page
│   └── test_api.py                    # API test: Add card via /api/PaymentMethods
│
├── utils/                             # Utility modules
│   └── config.py                      # Credential loader with robust path resolution
│
└── scripts/                           # Standalone utilities
    └── diagnostic.py                  # Diagnostic tool for troubleshooting
```

---

## 🛠️ Architecture & Design

### Fixtures (conftest.py)
- **`user`** (session-scoped): Loads credentials from `tests/new-user.json`
- **`driver`** (session-scoped): Creates Chrome WebDriver with headless mode, 1920x1080 desktop view
- **`ensure_user_registered`** (session-scoped, autouse): Attempts automatic user registration (non-fatal)
- **`login`** (function-scoped, autouse): Auto-logs in before **every test**, handles overlays gracefully
  - Removes Angular Material overlays (`.cdk-overlay-backdrop`, `.mat-mdc-dialog-surface`)
  - Implements multi-level click fallbacks: normal click → JS click → remove overlays + JS click
  - Logs all steps (INFO for success, ERROR for failures with actionable messages)

### Page Object Model (pages/)
Each page encapsulates:
- Stable locators (IDs, CSS selectors preferred over XPath)
- Wait conditions for element readiness
- Action methods (click, fill, submit)
- Logging for debugging

### Tests
- **UI Test** (`test_payments_ui.py`): 
  - Prerequisite: Autouse login fixture ensures authenticated session
  - Navigates Account → My Account → Payment Methods
  - Fills card form (unique number, expiry, CVV, name)
  - Asserts card appears on page with last 4 digits visible
  
- **API Test** (`test_api.py`):
  - Extracts auth token from browser localStorage
  - POSTs unique card to `/api/PaymentMethods` with Bearer token
  - Verifies response status (200/201/204)
  - Validates JSON response structure

---

## 🔧 Key Features

✅ **Overlay Handling**: Aggressive JavaScript removal of blocking elements (Angular Material dialogs, backdrops)
✅ **Click Resilience**: Multi-level fallback strategy for flaky UI interactions
✅ **Logging**: INFO/DEBUG/ERROR logs with actionable messages for troubleshooting
✅ **Stable Locators**: Prefer IDs and CSS selectors (e.g., `By.ID, "navbarAccount"`)
✅ **Error Recovery**: Non-fatal exceptions in fixtures allow tests to continue
✅ **Path Resolution**: `utils/config.py` searches multiple paths for credentials file
✅ **Pinned Dependencies**: All package versions fixed (e.g., selenium==4.15.2)
✅ **Documentation**: Comprehensive guides (SETUP.md, TESTING_GUIDE.md, REGISTRATION_REQUIRED.md)
✅ **CI/CD Ready**: `.github/workflows/test.yml` for GitHub Actions integration

---

## 📊 Test Execution Flow

```
1. pytest starts
   ↓
2. conftest.py fixtures load:
   - driver (session-scoped): Launch Chrome
   - user (session-scoped): Load creds from new-user.json
   - ensure_user_registered (session-scoped): Attempt auto-registration
   ↓
3. For each test function:
   - login (autouse): Navigate to home, log in, verify Logout button
   - [Test code runs] ← Can now use driver and user fixtures
   - login teardown: Log out (optional)
   ↓
4. After all tests:
   - driver teardown: Close browser
```

---

## ⚠️ Common Issues & Fixes

### Issue: Tests timeout on "Logout" button
**Cause**: Test user account (`aravindps987@gmail.com`) doesn't exist in Juice Shop
**Fix**: See `REGISTRATION_REQUIRED.md` – manually register account in browser

### Issue: ElementClickInterceptedException
**Cause**: Modal overlays blocking clicks (Angular Material CDK dialogs)
**Fix**: Already handled by `_remove_overlays()` and `_click_with_fallback()` in conftest.py. If persists, inspect element in DevTools and add to overlay selectors.

### Issue: ChromeDriver errors on macOS M1
**Cause**: ARM64 incompatibility
**Fix**: webdriver-manager handles this automatically. If issues persist, run container with `--platform linux/amd64`

### Issue: Credentials file not found
**Cause**: Relative path issue
**Fix**: `utils/config.py` now searches multiple paths. Verify `tests/new-user.json` exists with correct format: `{"email": "...", "password": "..."}`

---

## 🧪 Example Test Runs

### Run all tests with verbose output
```bash
pytest -v
```

### Run single test with stdout capture
```bash
pytest -v -s tests/test_payments_ui.py::test_add_card_ui
```

### Run with headless disabled (see browser)
Edit `tests/conftest.py` line ~35:
```python
# opts.add_argument("--headless=new")  # Comment out this line
```

### Run specific test file
```bash
pytest -v tests/test_api.py
```

---

## 📚 Additional Resources

- **SETUP.md**: Detailed Docker, Python, and credential setup
- **TESTING_GUIDE.md**: How to run tests and troubleshoot
- **REGISTRATION_REQUIRED.md**: Quick user registration guide
- **scripts/diagnostic.py**: Standalone script to verify setup (Juice Shop running, login works, overlays removable)

---

## 🔍 Troubleshooting

**Step 1**: Run diagnostic script
```bash
python scripts/diagnostic.py
```
Output confirms:
- ✓ Juice Shop running?
- ✓ Overlays removable?
- ✓ Login successful?

**Step 2**: Check logs
```bash
pytest -v -s tests/test_payments_ui.py 2>&1 | grep -E "ERROR|✓|✗"
```

**Step 3**: See `TESTING_GUIDE.md` for detailed steps

---

## 🚢 Deployment & CI/CD

GitHub Actions workflow (`.github/workflows/test.yml`) automatically runs tests on push. See file for configuration.

To enable:
1. Push to repository
2. GitHub Actions runs automatically
3. View results in "Actions" tab

---

## 📝 Notes for Reviewers

This project demonstrates:
- ✅ **Clean Architecture**: Modular POM, utils, fixtures
- ✅ **Robust Automation**: Overlay handling, click resilience, logging
- ✅ **Production-Ready**: Pinned deps, error handling, comprehensive docs
- ✅ **Best Practices**: Pytest fixtures, stable locators, non-fatal errors
- ✅ **Interview-Ready**: Clear code structure, well-documented thought process

---

## 📧 Contact

For questions or issues, open an issue on GitHub: https://github.com/psaravind29-code/juice-shop-testautomation/issues

---

**Last Updated**: November 2025
**Python Version**: 3.9+
**Selenium**: 4.15.2
**Pytest**: 7.4.3
