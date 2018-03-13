#!/bin/python
# -*- coding: utf-8 -*-
# author by xiexianbin@yovole.com
# function: sync google containers registory to docker.com.
# date 2018-3-10

import ConfigParser
from jinja2 import Template
import logging
import os
import platform
import subprocess
import sys
import yaml

## start log
# create logger
log_level = logging.DEBUG
formatter = logging.Formatter(
    fmt="%(asctime)-15s %(levelname)s %(process)d %(message)s - %(filename)s %(lineno)d",
    datefmt="%a %d %b %Y %H:%M:%S")

logger = logging.getLogger(name="googlecontainersmirrors")
logger.setLevel(log_level)

fh = logging.FileHandler(filename="googlecontainersmirrors.log")
fh.setLevel(log_level)
fh.setFormatter(formatter)
logger.addHandler(fh)

oh = logging.StreamHandler(sys.stdout)
oh.setLevel(log_level)
oh.setFormatter(formatter)
logger.addHandler(oh)
## end log

# define file path
IMAGES = ""


def _bash(command, force=False, debug=False):
    args = ['bash', '-c', command]

    _subp = subprocess.Popen(args, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    stdout, stderr = _subp.communicate()
    returncode = _subp.poll()
    print "Run bash: %s, ret is %s, stderr is \n%s" % \
        (command, returncode, stderr)

    if not stdout and not stderr:
        print "Run bash: %s, ret is %s" % (command, returncode)

    if force:
        return returncode, stdout, stderr
    return returncode


def main():
    logger.info("--- Begin to sync googlecontainersmirrors ---")

    # 1. copy mirror


    # 2. do sync


    # 3. update


    logger.info("--- End to sync googlecontainersmirrors ---")


if __name__ == '__main__':
    main()
