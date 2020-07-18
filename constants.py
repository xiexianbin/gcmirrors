#!/usr/bin/env python

import os


GCR_IMAGES = "https://raw.githubusercontent.com/xiexianbin/gcmirrors/sync/gcmirrors.txt"
DOCKER_TAGS_API_URL_TEMPLATE = {
    "docker.com": "https://registry.hub.docker.com/v1/repositories/%(repo)s/%(image)s/tags",
    "gcr.io": "https://gcr.io/v2/%(repo)s/%(image)s/tags/list"
}

GIT_TOKEN = os.environ.get("GIT_TOKEN", "")
GIT_USER = "xiexianbin"
GIT_REPO = "gcmirrors"
DOCKER_REPO = GIT_REPO
