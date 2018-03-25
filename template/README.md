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

| No | sync from | docker hub | count tags | total size | last sync time | more |
| - | - | - | - | - | - | - |
{% for index in range(len(images_list)) %}
| {{ index }} | https://gcr.io/google-containers/{{ images_list[index]['name'] }} | https://hub.docker.com/u/googlecontainersmirrors/{{ images_list[index]['name'] }}/tags/ | {{ len(images_list[index]['tags']) }} | {{ images_list[index]['total_size'] }} | {{ images_list[index]['date'] }} | [more](./google-containers/{{ images_list[index]['name'] }}) |
{% endfor %}

Support
-------

Email: me@xiexianbin.cn
