#!/usr/bin/env python3
"""
Defines shared data for all modules.
"""

CONGIF_PATH = None

# RE patterns
and_ = None
feat = None
feat2 = None
invalid = None


# Loggers
debugger = None
terminal = None

# Settings
settings = None

source = None
destination = None

set_source_docstring = """
Sets default source directory. This default value will be easily accessible
when performing any other tasks with this script that require a source. Note
that providing a non-existing path does not throw any errors. However, a
non-existing default path will not be accepted when other commands are run,
hence requiring the user to manually enter an existing source path.

    Usage:
        python3 handle_music.py set_source <path>

        Note that <path> can contain a tilde to shortcut the user directory.
        Both absolute and relative paths can be provided but an absolute
        representation will be stored in the settings.

        If no <path> is provided, this help message is printed.
"""

set_dest_docstring = """
Sets default destination directory. This default value will be easily
accessible when performing any other tasks with this script that require a
destination. Note that providing a non-existing path does not throw any
errors. However, a non-existing default path will not be accepted when other
commands are run, hence requiring the user to manually enter an existing
destination path.

    Usage:
        python3 handle_music.py set_dest <path>

        Note that <path> can contain a tilde to shortcut the user directory.
        Both absolute and relative paths can be provided but an absolute
        representation will be stored in the settings.

        If no <path> is provided, this help message is printed.
"""
