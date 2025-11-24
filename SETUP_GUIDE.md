# Setup & Execution Guide

**Last Updated:** November 24, 2025  
**For:** Test Automation Suite - Juice Shop Payment Methods

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Running Tests](#running-tests)
4. [Troubleshooting](#troubleshooting)
5. [CI/CD Integration](#cicd-integration)

---

## Prerequisites

### System Requirements
- **OS:** macOS, Linux, or Windows with WSL
- **Python:** 3.8+ (tested on 3.9.6)
- **Chrome:** Latest version
- **RAM:** 2GB minimum
- **Disk Space:** 500MB for dependencies

### Software Dependencies
- Git
- Python package manager (pip)
- Juice Shop application running locally

---

## Initial Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/psaravind29-code/juice-shop-testautomation.git
cd juice-shop-testautomation
```

### Step 2: Create Virtual Environment
```bash
# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**What gets installed:**
- `selenium==4.15.2` - WebDriver library
- `pytest==7.4.3` - Test framework
- `requests==2.31.0` - HTTP client
- `webdriver-manager==4.0.1` - ChromeDriver management

### Step 4: Create Test User Credentials
Create file: `tests/new-user.json`

```json
{
  "email": "your-test-user@example.com",
  "password": "your-secure-password",
  "firstName": "Test",
  "lastName": "User"
}
```

**Note:** This file is gitignored. Each developer should create their own.

### Step 5: Verify Juice Shop Is Running
```bash
curl http://localhost:3000
```

Expected response: HTML page or Juice Shop header

**If not running, start Juice Shop:**

Option A - Docker (Recommended):
```bash
docker run -d -p 3000:3000 bkimminich/juice-shop
```

Option B - Local Installation:
```bash
# Install from https://github.com/juice-shop/juice-shop
npm install
npm start
```

---

## Running Tests

### Quick Start (Recommended)
See tests run in Chrome browser with full output:

```bash
source .venv/bin/activate
HEADLESS=0 pytest -v tests/ -s
```

### All Commands

#### Run All Tests (Headless)
```bash
pytest -v tests/ -s
```

#### Run All Tests (Visible Browser)
```bash
HEADLESS=0 pytest -v tests/ -s
```

#### Run Specific Test
```bash
# Just the API test
pytest -v tests/test_api.py::test_add_card_api -s

# Just the UI test
pytest -v tests/test_payments_ui.py::test_add_card_ui -s
```

#### Run with Coverage Report
```bash
pytest -v tests/ -s --cov=tests --cov-report=html
# View: htmlcov/index.html
```

#### Run Tests Quietly
```bash
pytest tests/
```

#### Run Tests with Detailed Output
```bash
pytest -v tests/ -s --tb=short
```

---

## Understanding Test Output

### Success Output
```
tests/test_api.py::test_add_card_api ✓ Login successful
PASSED
tests/test_payments_ui.py::test_add_card_ui ✓ Login successful
PASSED

======================== 2 passed in 34.31s =========================
```

### Key Indicators
- ✅ Green checkmarks = Tests passing
- 🔴 Red X = Test failed
- ⏱️ Time duration = Test execution time
- "PASSED" = Test completed successfully
- "FAILED" = Test did not complete as expected

---

## Troubleshooting

### Issue: "FileNotFoundError: new-user.json not found"
**Solution:**
```bash
# Create the file with valid credentials
cat > tests/new-user.json << 'EOF'
{
  "email": "your-email@example.com",
  "password": "your-password",
  "firstName": "Test",
  "lastName": "User"
}
EOF
```

### Issue: "ConnectionError: Failed to establish connection"
**Solution:**
```bash
# Check if Juice Shop is running
curl http://localhost:3000

# If not, start it
docker run -d -p 3000:3000 bkimminich/juice-shop
```

### Issue: "TimeoutException: Element not found"
**Possible Causes:**
1. Juice Shop not fully loaded - wait longer
2. Page structure changed - update selectors
3. Element blocked by overlay - check overlay removal

**Solution:**
```bash
# Run with visible browser to debug
HEADLESS=0 pytest -v tests/ -s
```

### Issue: "ModuleNotFoundError: No module named 'selenium'"
**Solution:**
```bash
# Verify venv is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "ChromeDriver version mismatch"
**Solution:**
```bash
# webdriver-manager handles this automatically
# If still having issues:
pip install --upgrade webdriver-manager
```

### Issue: "Element click intercepted"
**Solution:**
This is already handled by `_remove_overlays()` function.
If still occurs:
```bash
# Run with visible browser to see what's blocking
HEADLESS=0 pytest -v tests/ -s
```

---

## File Structure

```
juice-shop-testautomation/
├── tests/
│   ├── conftest.py              # Fixtures & setup
│   ├── test_api.py              # API authentication test
│   ├── test_payments_ui.py       # UI navigation test
│   └── new-user.json            # Test credentials (gitignored)
├── pages/
│   ├── base_page.py             # Base page class
│   ├── login_page.py            # Login page object
│   ├── home_page.py             # Home page object
│   └── payments_page.py          # Payments page object
├── utils/
│   └── config.py                # Configuration helpers
├── README.md                     # Main documentation
├── TEST_PLAN.md                 # Test planning document
├── TEST_RESULTS.md              # Test execution results
├── SETUP_GUIDE.md              # This file
├── requirements.txt             # Python dependencies
└── .gitignore                   # Git ignore rules
```

---

## CI/CD Integration

### For GitHub Actions
Create `.github/workflows/test.yml`:

```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      juice-shop:
        image: bkimminich/juice-shop
        ports:
          - 3000:3000
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Create test user
      run: |
        cat > tests/new-user.json << 'EOF'
        {
          "email": "test@example.com",
          "password": "testpass123",
          "firstName": "Test",
          "lastName": "User"
        }
        EOF
    
    - name: Run tests
      run: pytest -v tests/ -s
```

### For Jenkins
```groovy
pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                sh 'python -m venv venv'
                sh '. venv/bin/activate && pip install -r requirements.txt'
            }
        }
        
        stage('Test') {
            steps {
                sh '. venv/bin/activate && pytest -v tests/ --junitxml=results.xml'
            }
        }
    }
    
    post {
        always {
            junit 'results.xml'
        }
    }
}
```

---

## Environment Variables

### HEADLESS
Controls browser visibility
```bash
HEADLESS=0   # Show browser (default for local testing)
HEADLESS=1   # Hide browser (default for CI/CD)
```

### Example
```bash
# Run with visible browser
HEADLESS=0 pytest -v tests/ -s

# Run headless
HEADLESS=1 pytest -v tests/ -s
```

---

## Best Practices

### Before Running Tests
- [ ] Activate virtual environment
- [ ] Juice Shop running and accessible
- [ ] Test credentials file exists
- [ ] Dependencies installed

### During Test Execution
- [ ] Do not close browser manually
- [ ] Do not interact with browser
- [ ] Keep system stable (no heavy processes)
- [ ] Check terminal for error messages

### After Test Execution
- [ ] Review test results
- [ ] Check for new issues
- [ ] Update documentation if needed
- [ ] Commit changes to git

---

## Useful Commands

### Check Environment
```bash
# Python version
python --version

# pytest version
pytest --version

# selenium version
pip show selenium

# Check if venv is active
which python
```

### View Test Logs
```bash
# Last 50 lines
pytest -v tests/ -s | tail -50

# Save to file
pytest -v tests/ -s > test_output.log
```

### Clean Up
```bash
# Remove cache
rm -rf .pytest_cache __pycache__

# Remove coverage
rm -rf htmlcov .coverage
```

---

## Support & Contacts

- **Repository:** https://github.com/psaravind29-code/juice-shop-testautomation
- **Issues:** Check GitHub issues page
- **Documentation:** See README.md and TEST_PLAN.md

---

**Setup Guide End**
