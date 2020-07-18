#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author by me@xiexianbin.cn
# function: sync google containers registory to docker.com.
# date 2018-3-10

import json
import os

from jinja2 import Template
from multiprocessing import Pool
from urllib import error as urllib_error

from utils import bash
from utils import get
from utils import logger
from utils import now
from utils import sort_versions
from constants import GCR_IMAGES
from constants import GIT_REPO
from constants import GIT_USER
from constants import GIT_TOKEN
from constants import DOCKER_REPO
from constants import DOCKER_TAGS_API_URL_TEMPLATE


TMP_PATH = '/tmp/{}'.format(GIT_REPO)
CURRENT_PATH = os.getcwd()


def _get_images_tags_list(domain, repo, image):
    _tags_list = []
    url = DOCKER_TAGS_API_URL_TEMPLATE[domain] % {"repo": repo, "image": image}
    try:
        resp = get(url)
        tags = json.loads(resp)
    except urllib_error.HTTPError as e:
        logger.warning("get url: {}, except: {}".format(url, e.reason))
        return _tags_list
    if domain == "docker.com":
        for t in tags:
            _tags_list.append(t.get("name"))
    elif domain == "gcr.io":
        _tags_list = tags.get("tags")

    # sort version:
    # major_version_number.minor_version_number.revision_number[-build_name.build_number]
    return sort_versions(_tags_list)


def _do_sync_image(
        source_domain, source_repo,
        target_domain, target_repo,
        image, tag):
    if source_domain == "docker.com":
        if source_repo == "":
            source_image = '{}:{}'.format(image, tag)
        else:
            source_image = '{}/{}:{}'.format(source_repo, image, tag)
    else:
        source_image = '{}/{}/{}:{}'.format(source_domain, source_repo, image, tag)

    if target_domain == "docker.com":
        target_image = '{}/{}:{}'.format(target_repo, image, tag)
    else:
        target_image = '{}/{}/{}:{}'.format(target_domain, target_repo, image, tag)

    logger.info("begin to sync image from {} to {}".format(source_image, target_image))

    # source
    bash('docker pull {}'.format(source_image))
    # tag
    bash('docker tag {} {}'.format(source_image, target_image))
    # push
    bash('docker push {}'.format(target_image))
    logger.info("sync image from {} to {} success.".format(source_image, target_image))

    # clean the docker file
    bash('docker system prune -f -a')


def _init_git():
    bash('git config user.name "xiexianbin"')
    bash('git config user.email "me@xiexianbin.cn"')

    if os.path.exists(TMP_PATH):
        bash('rm -rf {}'.format(TMP_PATH))
    os.chdir("/tmp")

    # clone master branch
    bash('git clone "https://{}@github.com/{}/{}.git"'.format(GIT_TOKEN, GIT_USER, GIT_REPO))

    os.chdir(CURRENT_PATH)


def _update_change(images_list):
    # for readme.md
    in_path = "./template/README.md"
    out_path = os.path.join(TMP_PATH, "README.md")
    with open(in_path, 'r') as in_file, open(out_path, 'w') as out_file:
        tmle = Template(in_file.read())
        out_file.write(tmle.render({
            "images_list": images_list,
            "image_count": len(images_list),
            "date": now()}))


def _push_git():
    os.chdir(TMP_PATH)
    bash('git add .')
    bash('git commit -m "auto sync gcr.io images to gcmirrors"')
    bash('git push --quiet "https://{}@github.com/{}/{}.git" '
         'master:master'.format(GIT_TOKEN, GIT_USER, GIT_REPO))


def _sync_image(image):
    logger.debug("Begin to sync image: [{}], sub pid is [{}]".format(image, os.getpid()))
    # source images tags
    gcr_image_tags = _get_images_tags_list(
        "gcr.io",
        "google_containers",
        image)
    # target images tags
    dockerhub_image_tags = _get_images_tags_list(
        "docker.com",
        DOCKER_REPO,
        image)

    for tag in gcr_image_tags:
        if tag in dockerhub_image_tags:
            logger.debug("image: {}:{}, is already sync.".format(image, tag))
            continue

        # do sync
        _do_sync_image(
            "gcr.io", "google_containers",
            "docker.com", DOCKER_REPO,
            image, tag)

    return "@@".join(gcr_image_tags)


def _do_sync():
    _target_images_list = get(GCR_IMAGES).split("\n")
    result_images_list = []

    logger.info("init multiprocessing pool, main pid is [{}]".format(os.getpid()))
    pp = Pool(5)
    subprocess_result = []
    for image in _target_images_list:
        image = image.replace("\n", "")
        subprocess_result.append(pp.apply_async(_sync_image, args=(image,)))

    for result in subprocess_result:
        r = result.get()
        gcr_image_tags = r.split("@@")

        result_images_list.append({
            "name": image,
            "tags": gcr_image_tags,
            "tags_count": len(gcr_image_tags),
            "total_size": "-",
            "date": now()})

    pp.close()
    pp.join()
    logger.info('All subprocess done.')

    return result_images_list


def do_sync():
    logger.info("--- Begin to sync gcmirrors ---")

    # 1. copy mirror
    _init_git()

    # 2. do sync
    result_images_list = _do_sync()

    # 3. update
    _update_change(result_images_list)

    # 4. push
    _push_git()

    logger.info("--- End to sync gcmirrors ---")


if __name__ == '__main__':
    do_sync()
