Google Containers Registry Mirrors [last sync {{ date }}]
-------

[![Sync Status](https://travis-ci.org/xiexianbin/googlecontainersmirrors.svg?branch=sync)](https://travis-ci.org/xiexianbin/googlecontainersmirrors)

Repository Address:

[https://hub.docker.com/u/googlecontainersmirrors/](https://hub.docker.com/u/googlecontainersmirrors/)


Useage
-------

From gcr.io:
```bash
docker pull gcr.io/google-containers/googlecontainersmirrors/hyperkube:v1.9.6
```

From Google Containers Registry Mirrors:
```bash
docker pull googlecontainersmirrors/hyperkube:v1.9.6
```

[SyncLog](./SyncLog.md)
-------

[Images](./google-containers/)
-------

Total of {{ image_count }}'s gcr.io images
-------

| No | sync from | docker hub | tags count | total size | last sync time | more |
| - | - | - | - | - | - | - |
{% for index in range(len(images_list)) %}
{% set image = images_list[index] %}
{% set name = image['name'] %}
{% set sync_from = "https://gcr.io/google-containers/%s" % name %}
{% set docker_hub = "https://hub.docker.com/u/google-containers/%s/tags/" % name %}
{% set total_count = image['total_count'] %}
{% set total_size = image['total_size'] %}
{% set date = image['date'] %}
{% set more = './google-containers/%s.md' % name %}
| {{ index }} | [{{ sync_from }}]({{ sync_from }}) | [{{ docker_hub }}]({{ docker_hub }}) | {{ tags_count }} | {{ total_size }} | {{ date }} | [more]({{ more }}) |
{% endfor %}

Support
-------

Email: me@xiexianbin.cn
