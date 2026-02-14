"""
Entry point for running the package as a module.

Usage:
    python -m unreal_dataset setup --config assets/house.json
    python -m unreal_dataset capture
    python -m unreal_dataset status
"""

import sys

from unreal_dataset.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
