Windows Troubleshooting Guide
=============================

This comprehensive guide addresses common issues Windows users encounter when installing and using ScanCode Toolkit. The solutions are tested on Windows 11 with Python 3.12, but most apply to Windows 10 as well.

Section 1: PowerShell Execution Policy Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Symptoms and Error Messages
~~~~~~~~~~~~~~~~~~~~~~~~~~~

You may encounter these errors when running PowerShell scripts:

.. code-block:: text

    scripts\configure.ps1 : File C:\path\to\scancode-toolkit\scripts\configure.ps1 cannot be loaded because 
    running scripts is disabled on this system. For more information, see about_Execution_Policies at 
    https:/go.microsoft.com/fwlink/?LinkID=135170.

    At line:1 char:1
    + scripts\configure.ps1
    + ~~~~~~~~~~~~~~~~~~~~~~
        + CategoryInfo          : SecurityError: (:) [], PSSecurityException
        + FullyQualifiedErrorId : UnauthorizedAccess

Solution with Set-ExecutionPolicy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning:: Changing execution policies affects system security. Only modify for trusted scripts.

**Temporary Solution (Current Session Only):**

.. code-block:: powershell

    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

**Permanent Solution (Current User):**

.. code-block:: powershell

    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

**Verify Current Policy:**

.. code-block:: powershell

    Get-ExecutionPolicy -List

Explanation of Security Implications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Restricted**: No scripts can run (default)
- **AllSigned**: Only scripts signed by trusted publishers can run
- **RemoteSigned**: Local scripts run freely; downloaded scripts must be signed
- **Unrestricted**: All scripts run (security risk)

For ScanCode Toolkit, ``RemoteSigned`` provides a good balance of security and functionality.

Section 2: Virtual Environment Activation Problems
--------------------------------------------------

Common Activation Errors
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    venv\Scripts\activate.ps1 : File C:\path\to\venv\Scripts\activate.ps1 cannot be loaded because 
    running scripts is disabled on this system.

    venv\Scripts\activate : The term 'venv\Scripts\activate' is not recognized as the name of a cmdlet, 
    function, script file, or operable program.

Multiple Solutions
~~~~~~~~~~~~~~~~~~

**Solution 1: Use Full Path with PowerShell**

.. code-block:: powershell

    # Navigate to scancode-toolkit directory first
    cd "C:\path\to\scancode-toolkit"
    
    # Activate with full path
    .\venv\Scripts\Activate.ps1

**Solution 2: Use Command Prompt (cmd) Instead**

.. code-block:: bat

    # In Command Prompt
    cd "C:\path\to\scancode-toolkit"
    venv\Scripts\activate.bat

**Solution 3: Create Activation Script**

Create ``activate-venv.ps1`` in the project root:

.. code-block:: powershell

    # activate-venv.ps1
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    & "$ScriptDir\venv\Scripts\Activate.ps1"

Then run:

.. code-block:: powershell

    .\activate-venv.ps1

How to Verify Activation Worked
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Check that your prompt shows ``(venv)`` and verify Python location:

.. code-block:: powershell

    # Should show (venv) prefix in prompt
    python -c "import sys; print(sys.executable)"
    
    # Should point to your venv directory
    # Expected: C:\path\to\scancode-toolkit\venv\Scripts\python.exe

Section 3: Python Not Found Errors
-----------------------------------

How to Check Python Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: powershell

    # Check if Python is installed
    python --version
    
    # Alternative command
    py --version
    
    # Check Python location
    where python
    
    # Check Python 3 specifically
    python3 --version

Adding Python to PATH (Step-by-Step)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Find Python Installation Directory:**

.. code-block:: powershell

    where python
    # Example output: C:\Users\Username\AppData\Local\Programs\Python\Python312\python.exe

2. **Add to Environment Variables:**

   - Press ``Win + R``, type ``sysdm.cpl``, press Enter
   - Go to **Advanced** tab → **Environment Variables**
   - Under **System variables**, find ``Path``, click **Edit**
   - Click **New** and add Python directory (e.g., ``C:\Users\Username\AppData\Local\Programs\Python\Python312``)
   - Click **New** again and add Scripts directory (e.g., ``C:\Users\Username\AppData\Local\Programs\Python\Python312\Scripts``)
   - Click **OK** on all windows

3. **Restart PowerShell** and verify:

.. code-block:: powershell

    python --version
    pip --version

Verifying pip Installation
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: powershell

    pip --version
    python -m pip --version
    
    # If pip is missing, install it
    python -m ensurepip --upgrade
    python -m pip install --upgrade pip

Section 4: Pip Installation Failures
-------------------------------------

Upgrading pip
~~~~~~~~~~~~~

.. code-block:: powershell

    python -m pip install --upgrade pip

Installing Visual C++ Build Tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Many Python packages require compilation. Install Visual C++ Build Tools:

1. Download `Visual Studio Build Tools <https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio>`_
2. Run the installer
3. Select **"C++ build tools"** workload
4. Check optional components:
   - **MSVC v143 - VS 2022 C++ x64/x86 build tools**
   - **Windows 11 SDK** (latest version)
5. Click **Install**

Using Pre-built Wheels
~~~~~~~~~~~~~~~~~~~~~~~

If compilation fails, try pre-built wheels:

.. code-block:: powershell

    # Use --only-binary=:all: to force wheel usage
    pip install --only-binary=:all: package-name
    
    # For ScanCode dependencies
    pip install --only-binary=:all: -r requirements.txt

Section 5: Configure Script Failures
-------------------------------------

Running as Administrator
~~~~~~~~~~~~~~~~~~~~~~

.. warning:: Only use Administrator privileges when necessary.

Right-click PowerShell and select **"Run as Administrator"**, then:

.. code-block:: powershell

    cd "C:\path\to\scancode-toolkit"
    scripts\configure.ps1

Cleaning Previous Attempts
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: powershell

    # Remove existing venv
    Remove-Item -Recurse -Force venv
    
    # Clean pip cache
    pip cache purge
    
    # Remove build artifacts
    Remove-Item -Recurse -Force build
    Remove-Item -Recurse -Force dist

Using --clean Option
~~~~~~~~~~~~~~~~~~~~

.. code-block:: powershell

    scripts\configure.ps1 --clean

Section 6: Long Path Issues in Windows
---------------------------------------

Enabling Long Path Support via Group Policy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Press ``Win + R``, type ``gpedit.msc``, press Enter
2. Navigate to: **Computer Configuration** → **Administrative Templates** → **System** → **Filesystem**
3. Find **"Enable Win32 long paths"** policy
4. Double-click and select **"Enabled"**
5. Click **OK** and restart your computer

Alternative: Shorter Installation Path
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install ScanCode Toolkit in a shorter path:

.. code-block:: powershell

    # Instead of: C:\Users\Username\OneDrive\Desktop\ScanCode Toolkit\scancode-toolkit
    # Use: C:\scancode-toolkit
    
    cd C:\
    git clone https://github.com/aboutcode-org/scancode-toolkit.git
    cd scancode-toolkit

Section 7: Antivirus and Windows Defender
-----------------------------------------

Adding Folder Exclusions
~~~~~~~~~~~~~~~~~~~~~~~~

1. Open **Windows Security** (search "Windows Security" in Start menu)
2. Go to **Virus & threat protection**
3. Click **Manage settings** under "Virus & threat protection settings"
4. Scroll to **Exclusions** and click **Add or remove exclusions**
5. Click **Add an exclusion** → **Folder**
6. Add your ScanCode Toolkit directory
7. Also add your Python venv directory

Temporary Disabling for Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning:: Only disable antivirus temporarily and re-enable immediately after installation.

1. In **Windows Security**, go to **Virus & threat protection**
2. Click **Manage settings**
3. Turn off **Real-time protection** temporarily
4. Complete ScanCode installation
5. **Immediately re-enable** real-time protection

Section 8: Performance Optimization
-----------------------------------

SSD Usage
~~~~~~~~~~

For optimal performance:

- Install ScanCode Toolkit on an SSD drive
- Use SSD for temporary files and virtual memory
- Ensure sufficient free space (at least 10GB for large scans)

Parallel Scanning Options
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: powershell

    # Use multiple processes for faster scanning
    scancode --processes 4 /path/to/scan
    
    # Adjust based on your CPU cores
    # For 8-core CPU: --processes 6 (leave 2 cores for system)

Disabling Search Indexing
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Right-click your ScanCode directory
2. Select **Properties**
3. Click **Advanced** under "Attributes"
4. Uncheck **"Allow files in this folder to have contents indexed in addition to file properties"**
5. Choose **"Apply changes to this folder, subfolders and files"**
6. Click **OK**

Section 9: Quick Diagnostic Script
----------------------------------

PowerShell Script to Check All Prerequisites
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create ``diagnose.ps1`` in your project root:

.. code-block:: powershell

    # diagnose.ps1
    Write-Host "ScanCode Toolkit Diagnostic Tool" -ForegroundColor Green
    Write-Host "==================================" -ForegroundColor Green
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "✗ Python not found" -ForegroundColor Red
        Write-Host "  Install Python from https://python.org" -ForegroundColor Yellow
    }
    
    # Check pip
    try {
        $pipVersion = pip --version 2>&1
        Write-Host "✓ pip: $pipVersion" -ForegroundColor Green
    } catch {
        Write-Host "✗ pip not found" -ForegroundColor Red
        Write-Host "  Run: python -m ensurepip --upgrade" -ForegroundColor Yellow
    }
    
    # Check venv
    if (Test-Path "venv") {
        Write-Host "✓ Virtual environment exists" -ForegroundColor Green
        
        # Check if activated
        $pythonPath = python -c "import sys; print(sys.executable)" 2>&1
        if ($pythonPath -like "*venv*") {
            Write-Host "✓ Virtual environment activated" -ForegroundColor Green
        } else {
            Write-Host "⚠ Virtual environment not activated" -ForegroundColor Yellow
            Write-Host "  Run: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
        }
    } else {
        Write-Host "✗ Virtual environment not found" -ForegroundColor Red
        Write-Host "  Run: python -m venv venv" -ForegroundColor Yellow
    }
    
    # Check scancode installation
    try {
        $scancodeVersion = scancode --version 2>&1
        Write-Host "✓ ScanCode: $scancodeVersion" -ForegroundColor Green
    } catch {
        Write-Host "✗ ScanCode not installed" -ForegroundColor Red
        Write-Host "  Run: pip install -e ." -ForegroundColor Yellow
    }
    
    # Check pytest
    try {
        $pytestVersion = pytest --version 2>&1
        Write-Host "✓ pytest: $pytestVersion" -ForegroundColor Green
    } catch {
        Write-Host "⚠ pytest not found (optional for testing)" -ForegroundColor Yellow
        Write-Host "  Run: pip install pytest" -ForegroundColor Yellow
    }
    
    # Check execution policy
    $policy = Get-ExecutionPolicy -Scope CurrentUser
    if ($policy -eq "Restricted") {
        Write-Host "⚠ Execution policy: $policy" -ForegroundColor Yellow
        Write-Host "  Run: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    } else {
        Write-Host "✓ Execution policy: $policy" -ForegroundColor Green
    }
    
    Write-Host "`nDiagnostic complete!" -ForegroundColor Green

Run the diagnostic:

.. code-block:: powershell

    .\diagnose.ps1

Section 10: Common Error Messages and Solutions
------------------------------------------------

"Permission Denied"
~~~~~~~~~~~~~~~~~~~~~

**Error:** ``PermissionError: [Errno 13] Permission denied``

**Solutions:**

1. **Run as Administrator:**

.. code-block:: powershell

    # Right-click PowerShell and "Run as Administrator"

2. **Check File Permissions:**

.. code-block:: powershell

    # Take ownership of the directory
    takeown /f "C:\path\to\scancode-toolkit" /r /d y
    
    # Grant full permissions
    icacls "C:\path\to\scancode-toolkit" /grant "${env:USERNAME}:(OI)(CI)F" /t

"SSL Certificate" Errors
~~~~~~~~~~~~~~~~~~~~~~

**Error:** ``SSL: CERTIFICATE_VERIFY_FAILED``

**Solutions:**

1. **Update certificates:**

.. code-block:: powershell

    pip install --upgrade certifi

2. **Use trusted hosts (temporary workaround):**

.. code-block:: powershell

    pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org package-name

3. **Configure corporate proxy (if applicable):**

.. code-block:: powershell

    $env:HTTPS_PROXY = "http://proxy.company.com:8080"
    $env:HTTP_PROXY = "http://proxy.company.com:8080"

"Path Too Long"
~~~~~~~~~~~~~~~

**Error:** ``File name too long`` or ``The specified path, file name, or both are too long``

**Solutions:**

1. **Enable long path support** (see Section 6)
2. **Use shorter installation path**
3. **Use subst command:**

.. code-block:: powershell

    subst S: "C:\Users\Username\OneDrive\Desktop\ScanCode Toolkit\scancode-toolkit"
    cd S:
    # Now work from S: drive

"scancode not found"
~~~~~~~~~~~~~~~~~~~~

**Error:** ``'scancode' is not recognized as an internal or external command``

**Solutions:**

1. **Check if virtual environment is activated:**

.. code-block:: powershell

    # Should show (venv) in prompt
    .\venv\Scripts\Activate.ps1

2. **Install ScanCode in development mode:**

.. code-block:: powershell

    pip install -e .

3. **Check installation:**

.. code-block:: powershell

    pip list | findstr scancode

Additional Resources
--------------------

- `ScanCode Toolkit Documentation <https://scancode-toolkit.readthedocs.io/>`_
- `Python for Windows Guide <https://docs.python.org/3/using/windows.html>`_
- `PowerShell Execution Policies <https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies>`_

If you encounter issues not covered in this guide, please:

1. Check the `ScanCode GitHub Issues <https://github.com/aboutcode-org/scancode-toolkit/issues>`_
2. Run the diagnostic script and include the output
3. Provide your Windows version, Python version, and exact error messages
