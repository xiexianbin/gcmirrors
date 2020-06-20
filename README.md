# gcr.io mirrors

[![Sync Status](https://travis-ci.org/xiexianbin/gcmirrors.svg?branch=sync)](https://travis-ci.org/xiexianbin/gcmirrors)

[https://hub.docker.com/u/gcmirrors](https://hub.docker.com/u/gcmirrors)

gcmirrors.txt from [https://console.cloud.google.com/gcr/images/google-containers/GLOBAL](https://console.cloud.google.com/gcr/images/google-containers/GLOBAL)


## Parameter

```
DOCKER_USER=xianbinxie
DOCKER_USER_PASSWORD=
GIT_TOKEN=
```


## Run

```
docker login -u${DOCKER_USER} -p${DOCKER_USER_PASSWORD}
pip install jinja2
python sync.py
```
