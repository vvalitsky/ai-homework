#!/usr/bin/env python3
"""
Quick test that Task3 script runs without semaphore warnings
"""

import subprocess
import sys
import os

script_path = os.path.join("Task3", "build_index.py")

print("Running Task3 build_index.py...")
result = subprocess.run(
    [sys.executable, script_path],
    capture_output=True,
    text=True,
    timeout=300,
)

print("STDOUT:")
print(result.stdout)

if result.stderr:
    print("\nSTDERR:")
    print(result.stderr)

# Check for the warning
if "resource_tracker" in result.stderr:
    print("\n⚠️  WARNING: Semaphore warning still present:")
    print(result.stderr)
    sys.exit(1)
elif result.returncode == 0:
    print("\n✓ Task3 completed successfully without resource warnings!")
    sys.exit(0)
else:
    print(f"\n❌ Task3 failed with exit code {result.returncode}")
    sys.exit(result.returncode)
