# Quick Registration Guide

## Problem
Tests are timing out because the test user account **does not exist** in your Juice Shop instance.

## Solution: Register Account (5 seconds)

1. **Open** http://localhost:3000 in your browser
2. **Click** "Account" button in top-right navbar
3. **Click** "Create Account"
4. **Fill the form:**
   - Email: `aravindps987@gmail.com`
   - Password: `cat@123`
   - Repeat Password: `cat@123`
   - Security Question: Pick any question (e.g., "What is your favorite color?")
   - Security Answer: Type any answer (e.g., "blue")
5. **Click** "Register"
6. You should see a success message and be logged in

## Verify It Worked
Run the test again:
```bash
pytest -q tests/test_payments_ui.py::test_add_card_ui -v
```

If you see `FAILED` with TimeoutException on "Payment Methods", the account still doesn't exist.
If you see `PASSED`, registration worked! ✓

## Why This Happens
The `ensure_user_registered` fixture in `conftest.py` tries to auto-register, but it's not 100% reliable with the Juice Shop UI. Manual registration is the safest approach.

---

**⏱️ Expected time:** 5 seconds
**After registration:** All tests should pass immediately
