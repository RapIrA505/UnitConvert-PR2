"""Use CPython's fallback OS metadata on Windows, avoiding failing WMI calls.

This affects platform metadata only, not application calculations or assertions.
Activated only by the verification scripts through PYTHONPATH.
"""
import sys

if sys.platform == "win32":
    sys.modules["_wmi"] = None
