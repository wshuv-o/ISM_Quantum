"""Path + environment bootstrap for experiment scripts. Import this first."""

import os
import sys

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OQS_INSTALL_PATH", os.path.expanduser("~/_oqs"))

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

RESULTS = os.path.join(REPO, "results")
os.makedirs(RESULTS, exist_ok=True)
