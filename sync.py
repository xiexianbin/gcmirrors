#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author by me@xiexianbin.cn
# function: sync google containers registory to docker.com.
# date 2018-3-10

import datetime
from jinja2 import Template
import json
import logging
import os
import subprocess
import sys
import urllib2

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
GCR_IMAGES = "https://raw.githubusercontent.com/xiexianbin/googlecontainersmirrors/sync/googlecontainersmirrors.txt"

GIT_TOKEN=os.environ.get("GIT_TOKEN", "")
GIT_USER="xiexianbin"
GIT_REPO="googlecontainersmirrors"
DOCKER_REPO=GIT_REPO
TMP_PATH='/tmp/googlecontainersmirrors'

DOCKER_TAGS_API_URL_TEMPLATE = {
    "docker.com": "https://registry.hub.docker.com/v1/repositories/%(repo)s/%(image)s/tags",
    "gcr.io": "https://gcr.io/v2/%(repo)s/%(image)s/tags/list"
}


def _bash(command, force=False, debug=False):
    args = ['bash', '-c', command]

    _subp = subprocess.Popen(args, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    stdout, stderr = _subp.communicate()
    returncode = _subp.poll()
    logger.debug("Run bash: %s, ret is %s, stderr is: %s"
                 % (command, returncode, stderr))

    if force:
        return returncode, stdout, stderr
    return returncode


def _sort_versions(tags_list):
    _version_list = []
    for version in tags_list:
        # major_version_number.minor_version_number.revision_number[-build_name.build_number]
        v = version.split('-')
        if '.' in v[0]:
            m_version = v[0].split('.')
            major_version_number = int(m_version[0].replace('v', ''))
            minor_version_number = int(m_version[1]) if isinstance(m_version[1], int) else m_version[1]
            try:
                revision_number = int(m_version[2]) if len(m_version) > 2 else ""
            except:
                revision_number = m_version[2]

            if len(v) == 2:
                b_version = v[1].split('.')
                build_name = b_version[0]
                try:
                    build_number = int(b_version[1]) if len(b_version) > 1 else ""
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
            versions = [v[0], '', '', '', '']
        _version_list.append(versions)
    _version_list = sorted(_version_list, key = lambda x: (x[0], x[1]))

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


def _get_images_tags_list(domain, repo, image):
    _tags_list = []
    url = DOCKER_TAGS_API_URL_TEMPLATE[domain] % {"repo": repo, "image": image}
    try:
        json_tags = json.load(urllib2.urlopen(url))
    except urllib2.HTTPError as e:
        logger.warn("get url: %s, except: %s"
                    % (url, e.msg))
        return _tags_list
    if domain == "docker.com":
        for t in json_tags:
            _tags_list.append(t.get("name"))
    elif domain == "gcr.io":
        _tags_list = json_tags.get("tags")

    if image in ["kubekins-test"]:
        return _tags_list
    else:
        # sort version:
        # major_version_number.minor_version_number.revision_number[-build_name.build_number]
        return _sort_versions(_tags_list)


def _sync_image(source_domain, source_repo,
                target_domain, target_repo,
                image, tag):
    if source_domain == "docker.com":
        if source_repo == "":
            source_image = '%s:%s' % (image, tag)
        else:
            source_image = '%s/%s:%s' % (source_repo, image, tag)
    else:
        source_image = '%s/%s/%s:%s' % (source_domain, source_repo, image, tag)

    if target_domain == "docker.com":
        target_image = '%s/%s:%s' % (target_repo, image, tag)
    else:
        target_image = '%s/%s/%s:%s' % (target_domain, target_repo, image, tag)

    logger.info("begin to sync image from %s to %s"
                % (source_image, target_image))

    # source
    _bash('docker pull %s' % source_image)
    # tag
    _bash('docker tag %s %s' % (source_image, target_image))
    # push
    _bash('docker push %s' % target_image)

    # clean the docker file
    _bash('docker system prune -f -a')


def _init_git():
    _bash('git config user.name "xiexianbin"')
    _bash('git config user.email "me@xiexianbin.cn"')

    # clone master branch
    _bash('git clone "https://%s@github.com/%s/%s.git"'
          % (GIT_TOKEN, GIT_USER, GIT_REPO))


def _update_change(images_list):
    os.makedirs(TMP_PATH)

    # for readme.md
    in_path = "./template/README.md"
    out_path = os.path.join(TMP_PATH, "README.md")
    with open(in_path, 'r') as in_file, open(out_path, 'w') as out_file:
        tmle = Template(in_file.read())
        out_file.write(tmle.render(images_list))


def _push_git():
    os.chdir(TMP_PATH)
    _bash('git config user.name "xiexianbin"')
    _bash('git add .')
    _bash('git commit -m "auto sync gcr.io images to googlecontainersmirrors"')
    _bash('git push --quiet "https://${GH_TOKEN}@github.com/%s/%s.git" master:master'
          % (GIT_TOKEN, GIT_USER, GIT_REPO))


def _do_sync():
    images_list = []
    for image in urllib2.urlopen(GCR_IMAGES):
        image = image.replace("\n", "")
        logger.debug("Begin to sync image: [%s]" % image)

        # source images tags
        gcr_image_tags = _get_images_tags_list("gcr.io", "google_containers", image)
        # target images tags
        dockerhub_image_tags = _get_images_tags_list("docker.com", DOCKER_REPO, image)

        for tag in gcr_image_tags:
            if tag in dockerhub_image_tags:
                logger.debug("image: %s:%s, is already sync." % (image, tag))
                continue

            # do sync
            _sync_image("gcr.io", "google_containers",
                        "docker.com", DOCKER_REPO,
                        image, tag)

        images_list.append({"name": image,
                            "tags": gcr_image_tags,
                            "total_size": "unkonw",
                            "date": datetime.datetime.now()})

    return images_list


def main():
    logger.info("--- Begin to sync googlecontainersmirrors ---")

    # 1. copy mirror
    _init_git()

    # 2. do sync
    images_list = _do_sync()

    # 3. update
    _update_change(images_list)

    # 4. push
    _push_git()

    logger.info("--- End to sync googlecontainersmirrors ---")


if __name__ == '__main__':
    main()
