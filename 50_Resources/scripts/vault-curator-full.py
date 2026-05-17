#!/usr/bin/env python3
"""Vault Curator - Full pipeline: Stats + Index updates.

This script runs inside the vault repository so it gets synced."""
import subprocess, sys, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def run(script_name):
    path = os.path.join(SCRIPT_DIR, script_name)
    print(f"\n=== Running {script_name} ===")
    result = subprocess.run([sys.executable, path], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("ERRORS:", result.stderr, file=sys.stderr)
    return result.returncode == 0

if __name__ == "__main__":
    run("vault-curator-collect.py")
    run("update-indices.py")
