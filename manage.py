#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import tempfile


def main():
    os.environ["DJANGO_SETTINGS_MODULE"] = "vgloss.settings"

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Install dummy database for makemigrations, since we won't actually have a
    # database, but it wants one for doing some checks.
    if sys.argv[1] == "makemigrations":
        os.environ["VGLOSS_DUMMY_DATABASE"] = "true"

    if sys.argv[1] == "test":
        with tempfile.TemporaryDirectory() as testdir:
            os.environ["VGLOSS_BASE"] = testdir
            execute_from_command_line(sys.argv)
    else:
        execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
