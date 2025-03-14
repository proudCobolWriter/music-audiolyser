# Imports
import sys

# Constants
REQUIRED_PY_VERSION = "3.9.18"

# Starting the node/webserver
if sys.version_info[0:3] != tuple(REQUIRED_PY_VERSION.replace(".", "")):
    raise UserWarning(f"The interpreter is running the wrong version of python (currently: {".".join(map(str, sys.version_info[0:3]))}) which could cause issues with Essentia.\nConsider using the {REQUIRED_PY_VERSION} one")

if __name__ == "__main__":
    pass