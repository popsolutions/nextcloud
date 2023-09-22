#!/usr/bin/python3
"""Set Nextcloud admin password and domain to serve

Option:
    --pass=     unless provided, will ask interactively
    --domain=   unless provided, will ask interactively
                DEFAULT=www.example.com
"""

import sys
import getopt
import subprocess

from subprocess import call
from os.path import *
from os import chdir
from libinithooks.dialog_wrapper import Dialog

DEFAULT_DOMAIN = "www.example.com"


def usage(s=None):
    if s:
        print("Error:", s, file=sys.stderr)
    print("Syntax: %s [options]" % sys.argv[0], file=sys.stderr)
    print(__doc__, file=sys.stderr)
    sys.exit(1)


def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "h",
                                       ['help', 'pass=', 'domain='])
    except getopt.GetoptError as e:
        usage(e)

    password = ""
    domain = ""
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt == '--pass':
            password = val
        elif opt == '--domain':
            domain = val

    if not password:
        d = Dialog('TurnKey GNU/Linux - First boot configuration')
        prefix = ''
        while True:
            password = d.get_password(
                "Nextcloud Password",
                prefix + "Enter new password for the Nextcloud 'admin' account.",
                pass_req=10)
            try:
                subprocess.run(
                         args = ['/usr/local/bin/turnkey-occ', 'user:resetpassword', '--password-from-env', 'admin'],
                         cwd='/var/www/nextcloud',
                         env={"OC_PASS": password},
                         text=True,
                         capture_output=True,
                         check=True)
            except subprocess.CalledProcessError as e:
                prefix = e.stderr + e.stdout + '\n'
            else:
                break
    else:
        subprocess.run(
                 args = ['/usr/local/bin/turnkey-occ', 'user:resetpassword', '--password-from-env', 'admin'],
                 cwd='/var/www/nextcloud',
                 env={"OC_PASS": password},
                 text=True)


    if not domain:
        if 'd' not in locals():
            d = Dialog('TurnKey GNU/Linux - First boot configuration')

        domain = d.get_input(
            "Nextcloud Domain",
            "Enter the domain to serve Nextcloud.",
            DEFAULT_DOMAIN)

    if domain == "DEFAULT":
        domain = DEFAULT_DOMAIN

    sedcom = """
        /0 => 'localhost',/ a\
    1 => '%s',
    """

    conf = '/var/www/nextcloud/config/config.php'
    call(['sed', '-i', "/1 => /d", conf])
    call(['sed', '-i', sedcom % domain, conf])

if __name__ == "__main__":
    main()
