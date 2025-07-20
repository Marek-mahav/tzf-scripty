# tests/conftest.py
import sys, os

# 1) koreň projektu (o úroveň vyššie než tests/)
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root not in sys.path:
    sys.path.insert(0, root)

# 2) priečinok script_a, kde máš dashboard.py aj podsložku modules/
script_a = os.path.join(root, "script_a")
if script_a not in sys.path:
    sys.path.insert(0, script_a)
