# verify_setup.py
import subprocess
import shutil

def verify_setup():
    print("=" * 60)
    print("VERIFYING TEST SETUP")
    print("=" * 60)
    
    # Check ChromeDriver
    print("1. Checking ChromeDriver...")
    chromedriver_path = shutil.which("chromedriver")
    if chromedriver_path:
        print(f"   ✓ ChromeDriver found at: {chromedriver_path}")
        try:
            result = subprocess.run(
                ["chromedriver", "--version"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                print("   ✓ ChromeDriver is working")
            else:
                print("   ✗ ChromeDriver found but not working")
        except:
            print("   ✗ ChromeDriver found but blocked by macOS")
    else:
        print("   ✗ ChromeDriver not found in PATH")
    
    # Check Chrome browser
    print("\n2. Checking Chrome browser...")
    chrome_path = shutil.which("google-chrome") or shutil.which("chrome")
    if chrome_path:
        print(f"   ✓ Chrome browser found at: {chrome_path}")
    else:
        print("   ℹ Chrome browser not in PATH (may be in Applications)")
    
    # Check test files
    print("\n3. Checking test files...")
    import os
    test_files = [
        "tests/new-user.json",
        "tests/test_payments_ui.py", 
        "tests/test_api.py"
    ]
    
    for file in test_files:
        if os.path.exists(file):
            print(f"   ✓ {file} exists")
        else:
            print(f"   ✗ {file} missing")
    
    print("\n" + "=" * 60)
    print("SETUP STATUS:")
    
    if chromedriver_path:
        print("✓ READY - Try running: pytest -v tests/test_payments_ui.py -s")
    else:
        print("✗ NOT READY - Install ChromeDriver first:")
        print("  brew install chromedriver")
    
    print("=" * 60)

if __name__ == "__main__":
    verify_setup()