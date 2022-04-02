from shutil import which

import pytest


def onlyif_cmds_exist(*commands):
    """
    Decorator to skip test when at least one of `commands` is not found.
    """
    for cmd in commands:
        if not which(cmd):
            return pytest.mark.skip(
                "This test runs only if command '{}' " "is installed".format(cmd)
            )
    return lambda f: f
