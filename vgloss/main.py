import os
import sys
import argparse

from django import setup
from django.conf import settings
from django.core.management import call_command


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via input() and return True/False answer.

    From: https://stackoverflow.com/questions/3041986/apt-command-line-interface-like-yes-no-input#3041990
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def main():
    parser = argparse.ArgumentParser("Manage vgloss gallery")
    subparsers = parser.add_subparsers(title="command",
                                       dest="command")

    init_cmd = subparsers.add_parser("init",
                                     help="Initialize gallery")
    init_cmd.add_argument("--noinput",
                          action="store_true",
                          help="Don't ask for keyboard input")

    serve_cmd = subparsers.add_parser("serve",
                          help="Run webserver for gallery")
    serve_cmd.add_argument('--port', type=int, default="8000",
                           help='Port to listen on')

    subparsers.add_parser("scan",
                          help="Detect new images and process them.")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return -1

    os.environ["DJANGO_SETTINGS_MODULE"] = "vgloss.settings"
    if args.command != "init":
        setup()
        # Make sure BASE_DIR is an initialized gallery
        if not os.path.exists(settings.DATA_DIR):
            print("Directory is not a vgloss gallery:", file=sys.stderr)
            print(settings.BASE_DIR, file=sys.stderr)
            print('Run "vgloss init" to initialize it.', file=sys.stderr)
            sys.exit(-1)
        call_command("migrate", verbosity=0, interactive=False)

    return dict(
        init=command_init,
        serve=command_serve,
        scan=command_scan,
    )[args.command](args)

def command_init(args):
    print("Initializing vgloss gallery in: ", settings.BASE_DIR)
    if args.noinput:
        proceed = True
    else:
        proceed = query_yes_no("Are you sure?")
    if not proceed:
        return -1

    os.makedirs(settings.DATA_DIR, exist_ok=True)
    setup()
    call_command("migrate", verbosity=0, interactive=False)
    command_scan(args)

def command_serve(args):
    command_scan(args)
    return call_command("runserver", verbosity=1, addrport=str(args.port))

def command_scan(args):
    from vgloss.scan import scan_all
    from vgloss.thumbnail import generate_all_thumbnails
    scan_all()
    generate_all_thumbnails()
