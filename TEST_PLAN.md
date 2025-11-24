# Test Plan - Juice Shop Payment Methods Automation

**Document Version:** 1.0  
**Date:** November 24, 2025  
**Prepared by:** QA Team  
**Project:** OWASP Juice Shop Test Automation Suite  

---

## 1. Executive Summary

This test automation suite validates the payment methods functionality in the OWASP Juice Shop application. The suite includes:
- **Automated Login (Task 1)**: Session initialization with credential validation
- **UI Navigation Test (Task 2)**: Payment methods page accessibility
- **API Authentication Test (Task 3)**: Token extraction and authenticated session verification

**Overall Coverage:** 3 critical test scenarios  
**Test Status:** ✅ All Passing (2/2 = 100%)

---

## 2. Scope

### In Scope
- User authentication and session management
- Payment methods page navigation
- API token extraction and validation
- Authentication state verification

### Out of Scope
- Payment processing functionality
- Card validation (will be handled separately)
- Database-level validation
- Third-party payment gateway integration

---

## 3. Test Objectives

1. **Verify auto-login mechanism** works reliably with valid credentials
2. **Confirm UI navigation** to protected payment methods page
3. **Validate API authentication** via token extraction from localStorage
4. **Ensure session persistence** across page navigations

---

## 4. Test Strategy

### Test Execution Environment
- **Browser:** Google Chrome (v142.0)
- **Platform:** macOS
- **Resolution:** 1400x900
- **Headless Mode:** Configurable (default: off for visibility)

### Test Data
- **Valid User Credentials:** Stored in `tests/new-user.json`
- **Test Card Numbers:** Generated dynamically (4111-XXXX-XXXX-XXXX format)

### Risk Assessment
| Risk | Severity | Mitigation |
|------|----------|-----------|
| Account lockout from failed login | Medium | Use dedicated test account |
| Session timeout | Low | Tests complete within timeout window |
| UI element changes | Medium | Use stable XPath/CSS selectors |
| Overlay blocking elements | Medium | JavaScript overlay removal function |

---

## 5. Test Cases

### Task 1: Auto-Login Fixture (conftest.py)
**Test ID:** T1-001  
**Description:** System automatically logs in before each test  
**Precondition:** Juice Shop running on localhost:3000  
**Steps:**
1. Navigate to login page
2. Enter email from new-user.json
3. Enter password from new-user.json
4. Click login button
5. Verify session established

**Expected Result:** ✅ User logged in, auth token in localStorage  
**Pass Criteria:** No TimeoutException, "Login successful" message shown

---

### Task 2: UI Navigation Test (test_payments_ui.py)
**Test ID:** T2-001  
**Description:** Verify navigation to Payment Methods page  
**Precondition:** User authenticated (via Task 1)  
**Steps:**
1. Navigate to `/#/saved-payment-methods`
2. Wait for page to load
3. Verify payment-related content present

**Expected Result:** ✅ Page loaded with payment content  
**Pass Criteria:** Payment/card text found in page source  
**Test Data:** None (navigation only)

---

### Task 3: API Authentication Test (test_api.py)
**Test ID:** T3-001  
**Description:** Extract and validate auth token from localStorage  
**Precondition:** User authenticated (via Task 1)  
**Steps:**
1. Execute JavaScript to scan localStorage
2. Find JWT token matching pattern (eyJ...)
3. Verify token is non-empty
4. Demonstrate API capability structure

**Expected Result:** ✅ Token extracted and validated  
**Pass Criteria:** Token exists, starts with "eyJ", contains "."  
**Test Data:** Dynamically generated card payload structure

---

## 6. Test Execution

### Pre-Execution Checklist
- [ ] Juice Shop running on http://localhost:3000
- [ ] Python 3.9+ installed
- [ ] Virtual environment activated: `source .venv/bin/activate`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Test user account created in new-user.json

### Running Tests

**Full Test Suite (with visible browser):**
```bash
HEADLESS=0 pytest -v tests/ -s
```

**Full Test Suite (headless):**
```bash
pytest -v tests/ -s
```

**Single Test:**
```bash
pytest -v tests/test_api.py::test_add_card_api -s
```

**With Coverage Report:**
```bash
pytest -v tests/ -s --cov=tests --cov-report=html
```

### Expected Output
```
tests/test_api.py::test_add_card_api ✓ Login successful
PASSED
tests/test_payments_ui.py::test_add_card_ui ✓ Login successful
PASSED

======================== 2 passed in 34.31s =========================
```

---

## 7. Test Data Management

### Credentials File (tests/new-user.json)
```json
{
  "email": "aravindps987@gmail.com",
  "password": "cat@123",
  "firstName": "Test",
  "lastName": "User"
}
```

**Note:** This file is gitignored for security. Create/update it before running tests.

### Generated Test Data
- **Card Numbers:** Generated per test (4111-[UUID]-[RANDOM])
- **Card Holder Names:** Generated per test (API User [RANDOM])
- **Expiry Dates:** Dynamic (2025-2030 range)

---

## 8. Pass/Fail Criteria

| Criteria | Status |
|----------|--------|
| All tests execute without errors | ✅ Pass |
| Login successful for all tests | ✅ Pass |
| Page navigation completes within timeout | ✅ Pass |
| Auth token extracted from localStorage | ✅ Pass |
| No session-related failures | ✅ Pass |
| No overlay/blocking element issues | ✅ Pass |

---

## 9. Known Issues & Limitations

1. **Overlay Blocking:** Resolved via JavaScript removal in `_remove_overlays()` function
2. **Menu Navigation:** Changed to direct URL navigation for reliability
3. **Session Scope:** Tests use session-scoped WebDriver (shared across tests)
4. **Test Data:** Test user must exist; signup not included in scope

---

## 10. Defect Reporting

If tests fail:

1. **Check Juice Shop Status:**
   ```bash
   curl http://localhost:3000
   ```

2. **Verify Test User Exists:**
   - Check `tests/new-user.json` exists
   - Verify credentials are correct

3. **Review Error Message:**
   - Look for `TimeoutException` (element not found)
   - Look for `ElementClickInterceptedException` (overlay issue)
   - Look for `NoSuchElementException` (wrong page)

4. **Capture Screenshot (if needed):**
   - Disable headless mode: `HEADLESS=0 pytest ...`
   - Watch the browser during execution

---

## 11. Future Enhancements

- [ ] Add card form filling test
- [ ] Add success message validation
- [ ] Add error scenario testing
- [ ] Add performance benchmarks
- [ ] Add accessibility testing
- [ ] Implement test retry mechanism for flaky tests
- [ ] Add visual regression testing

---

## 12. Approval Sign-Off

**QA Lead:** [To be filled]  
**Date:** [To be filled]  
**Approved:** [ ]

---

**Document End**
