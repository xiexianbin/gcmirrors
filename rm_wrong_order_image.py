#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author by xiexianbin@yovole.com
# function: sync google containers registory to docker.com.
# date 2018-3-10

##
# EVN
# DOCKER_USER=xiexianbin
# DOCKER_PASSPORT=password
##

import json
import os

from urllib import error as urllib_error

from constants import GCR_IMAGES, DOCKER_REPO
from utils import logger
from utils import delete
from utils import get
from utils import post

ENV = os.environ

DOCKER_TAGS_API_URL_TEMPLATE = {
    "docker.com": "https://registry.hub.docker.com/v1/repositories/%(repo)s/%(image)s/tags",
    "gcr.io": "https://gcr.io/v2/%(repo)s/%(image)s/tags/list"
}


def _get_images_tags_list(domain, repo, image):
    tags_list = []
    url = DOCKER_TAGS_API_URL_TEMPLATE[domain] % {"repo": repo, "image": image}
    try:
        json_tags = json.loads(get(url))
    except urllib_error.HTTPError as e:
        logger.warn("get url: {}, except: {}".format(url, e.reason))
        return tags_list
    if domain == "docker.com":
        for t in json_tags:
            tags_list.append(t.get("name"))
    elif domain == "gcr.io":
        tags_list = json_tags.get("tags")
    return tags_list


def _get_token():
    data = {
        "username": ENV['DOCKER_USER'],
        "password": ENV['DOCKER_PASSPORT']}
    url = "https://hub.docker.com/v2/users/login/"

    response = post(url, data)
    token = json.loads(response).get("token")

    return token


def _del_image_by_tag(image, tag):
    # 1. get token
    token = _get_token()
    headers = {
        'Authorization': 'JWT {}'.format(token),
        'Content-Type': 'application/json'}
    url = "https://hub.docker.com/v2/repositories/{}/{}/tags/{}/".format(
        DOCKER_REPO, image, tag)
    try:
        resp = delete(url, headers)
        logger.debug("resp: {}".format(resp))
    except Exception as e:
        logger.debug("wrong delete {}:{}, except: {}".format(image, tag, e))


def _do_rm_wrong_order_image_tag():
    _target_images_list = get(GCR_IMAGES).split("\n")
    for image in _target_images_list:
        image = image.replace("\n", "")
        # target images tags
        dockerhub_image_tags = _get_images_tags_list(
            "docker.com", DOCKER_REPO, image)

        for tag in dockerhub_image_tags:
            if tag.startswith('v1.10'):
                logger.debug("Begin to delete image: [{}:{}]".format(image, tag))
                # delete docker images
                _del_image_by_tag(image, tag)


def do_delete():
    logger.info("--- Begin to delete wrong order image ---")

    # 2. do delete wrong order image tags
    # _do_rm_wrong_order_image_tag()
    # _get_token()
    # _del_image_by_tag('gcmirrors/hyperkube',
    #                   'v1.10.0-rc.1')
    _do_rm_wrong_order_image_tag()

    logger.info("--- End to delete wrong order image ---")


if __name__ == '__main__':
    do_delete()
