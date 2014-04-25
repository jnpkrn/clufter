#!/bin/sh
# Copyright 2013 Red Hat, Inc.                                                
# Part of clufter project                                                     
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

# Specific tests can be specified as per [1], e.g.:
#    tests.filter.XMLTraverse.testXSLTTemplate
# If nothing specified, auto-discovery is in place -> all the tests.
# ---
# [1] http://docs.python.org/2/library/unittest.html#command-line-interface

stop=$(printf "\033\[0m")
blue=$(printf "\033[01;34m") red=$(printf "\033[01;31m")
green=$(printf "\033[01;32m") cyan=$(printf "\033[01;36m")
magenta=$(printf "\033[01;35m")
COLORIZE='|& sed \
    -e "s/\(^\|[^A-Za-z]\)\(OK\)/\1${blue}\2${stop}/"      \
    -e "s/\(^\|[^A-Za-z]\)\(FAILED.*\)/\1${red}\2${stop}/" \
    -e "s/\(^\|[^A-Za-z]\)\(ok\)/\1${green}\2${stop}/"     \
    -e "s/^\(\(FAIL\|ERROR\):.*\)/${magenta}\1${stop}/"    \
    -e "s/\(^\|[^A-Za-z]\)\(FAIL\)/\1${red}\2${stop}/"     \
    -e "s/\(^\|[^A-Za-z]\)\(ERROR\)/\1${red}\2${stop}/"    \
    -e "s/^\(Ran [1-9][0-9]*.*\)/${cyan}\1${stop}/"'

if python -c "import sys; sys.exit(sys.version_info[:2] < (2,7))"; then
	CMD="python -m unittest"
else
	# pre-2.7 unittest doesn't offer test discovery, use external unittest2
	CMD="unit2"
fi
DEBUG="env LOGLEVEL=WARNING"
VERBOSE=1
ACC=
while [ $# -gt 0 ]; do
    case "$1" in
        "-d")
            DEBUG=
            ;;
        "-q")
            VERBOSE=0
            ;;
        *)
            ACC+=" $1"
            ;;
    esac
    shift
done
if [ -z ${ACC} ]; then
    ACC=" discover -s tests -p '*.py'"
    if [ "$VERBOSE" -eq 1 ]; then
        ACC+=" --verbose"
    fi
fi
if [ ! -t 0 ]; then
    COLORIZE=
fi
eval "$DEBUG $CMD $ACC $COLORIZE"
