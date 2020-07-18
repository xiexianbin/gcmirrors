#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author by me@xiexianbin.cn
# function: python utils.
# date 2020-7-18

import datetime
import logging
import sys
import subprocess
import traceback

from urllib import parse
from urllib import request
from urllib import error as urllib_error


def gen_logger():
    # create logger
    log_level = logging.DEBUG
    formatter = logging.Formatter(
        fmt="%(asctime)-15s %(process)d %(levelname)s %(message)s - %(filename)s %(lineno)d",
        datefmt="%a %d %b %Y %H:%M:%S")

    _logger = logging.getLogger(name="gcmirrors")
    _logger.setLevel(log_level)

    fh = logging.FileHandler(filename="gcmirrors.log")
    fh.setLevel(log_level)
    fh.setFormatter(formatter)
    _logger.addHandler(fh)

    oh = logging.StreamHandler(sys.stdout)
    oh.setLevel(log_level)
    oh.setFormatter(formatter)
    _logger.addHandler(oh)
    return _logger


logger = gen_logger()


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def bash(command, force=False, debug=False):
    args = ['bash', '-c', command]

    _sub_p = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = _sub_p.communicate()
    return_code = _sub_p.poll()
    logger.debug(
        "Run bash: {}, ret is %s, stderr is: {}".format(command, return_code, stderr))

    if not stdout and not stderr:
        logger.info("Run bash: %s, ret is %s" % (command, return_code))

    if force:
        return return_code, stdout, stderr
    return return_code


def get(url):
    try:
        return request.urlopen(url=url).read().decode('utf-8')
    except urllib_error.HTTPError:
        raise


def post(url, data, headers=None):
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    try:
        post_data = parse.urlencode(data).encode('utf8')
        req = request.Request(url, post_data)
        return request.urlopen(req, headers).read().decode('utf-8')
    except urllib_error.HTTPError:
        raise


def delete(url, headers=None):
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    try:
        req = request.Request(url=url, method="DELETE")
        return request.urlopen(req, headers).read().decode('utf-8')
    except urllib_error.HTTPError:
        raise


def sort_versions(tags_list):
    _version_list = []
    for version in tags_list:
        # major_version_number.minor_version_number.revision_number[-build_name.build_number]
        v = version.split('-')
        if '.' in v[0]:
            m_version = v[0].split('.')
            try:
                major_version_number = int(m_version[0].replace('v', ''))
            except:
                # cadvisor:v.25.0
                major_version_number = ""
            minor_version_number = int(m_version[1]) if isinstance(
                m_version[1], int) else m_version[1]
            try:
                revision_number = int(m_version[2]) if len(
                    m_version) > 2 else ""
            except:
                revision_number = m_version[2]

            if len(v) == 2:
                b_version = v[1].split('.')
                build_name = b_version[0]
                try:
                    build_number = int(b_version[1]) if len(
                        b_version) > 1 else ""
                except:
                    build_number = b_version[1]
            else:
                build_name = ''
                build_number = ''

            versions = [major_version_number,
                        minor_version_number,
                        revision_number,
                        build_name,
                        build_number]
        else:
            versions = [version, '', '', '', '']
        _version_list.append(versions)
    try:
        _version_list = sorted(_version_list, key=lambda x: (x[0], x[1]))
    except:
        logger.error("sort [{}] traceback: {}".format(_version_list, traceback.print_exc()))

    version_list = []
    for _v in _version_list:
        if _v[1] == '':
            version_list.append(_v[0])
        elif _v[2] == '':
            version_list.append("v%s.%s"
                                % (_v[0], _v[1]))
        elif _v[3] == '':
            version_list.append("v%s.%s.%s"
                                % (_v[0], _v[1], _v[2]))
        elif _v[4] == '':
            version_list.append("v%s.%s.%s-%s"
                                % (_v[0], _v[1], _v[2], _v[3]))
        else:
            version_list.append("v%s.%s.%s-%s.%s"
                                % (_v[0], _v[1], _v[2], _v[3], _v[4]))
    return version_list
