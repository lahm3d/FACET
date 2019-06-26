""" small module to change FACET parameters/config """

import os
import sys
from pathlib import Path

def get_config_path():
    config_dir = Path(os.path.dirname(os.path.abspath(__file__))) # get script directory
    file = config_dir / "config.ini" # construct config file path

    # check and return file path if true or exit
    if file.exists() is True:
        return file
    else:
        print("File does not exist or not found. Please recheck!")
        sys.exit(1)
