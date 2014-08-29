# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccs-obfuscate command"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..command import Command
from ..format import SimpleFormat


@Command.deco(('ccs-obfuscate-credentials',
                  ('ccs-obfuscate-identifiers')))
def ccs_obfuscate(cmd_ctxt,
                  input="/etc/cluster/cluster.conf",
                  output="./cluster.conf",
                  skip='none'):
    """Obfuscate credentials/IDs in CMAN-based cluster config.

    Either obfuscation pass can be suppressed by skip parameter, by
    default they are performed both in row.

    Following conventions are used for substituted ids/credentials:
    1. identifiers used for crosslinking (referential integrity)
       ought to be converted in a way not violating this integrity
    2. identifiers clearly out of referential integrity (i.e.,
       arbitrary value unrelated to the rest of the XML tree)
       ought to be substituted with strings starting with 'REL-'
    3. credentials ought to be substituted with strings starting
       with 'SECRET-'
    4. overall, any affected item should be substituted with
       capitalized string to visually emphasize the substitution

    Options:
        input   input CMAN-based cluster configuration file
        output  output file with obfuscated credentials/identifiers
        skip    pass to skip (none/ids/creds), neater than --noop
    """
    try:
        skip = ('creds', 'ids').index(skip.lower()) + 1
    except ValueError:
        skip = 0
    if skip == 1:
        cmd_ctxt['filter_noop'].append('ccs-obfuscate-credentials')
    if skip == 2:
        cmd_ctxt['filter_noop'].append('ccs-obfuscate-identifiers')

    FILE = SimpleFormat.FILE
    return (
        (FILE, input),
        (
            (FILE, output),
        )
    )
