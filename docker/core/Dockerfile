FROM debian:jessie

MAINTAINER Richard Bann "richard.bann@vertis.com"

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y upgrade

ENV LANG C.UTF-8

RUN set -x \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
       apt-get install -y --no-install-recommends \
           python3 \
           python3-pip \
    && pip3 install \
           click \
    && DEBIAN_FRONTEND=noninteractive \
       apt-get purge --auto-remove -y \
           python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY skel /etc/skel
COPY skel/* /root/
RUN groupadd -g 1000 delveloper && useradd -u 1000 -g 1000 -m developer
RUN groupadd -g 1001 postgres && useradd -u 1001 -g 1001 -m postgres
RUN groupadd -g 1002 django && useradd -u 1002 -g 1002 -m django
RUN groupadd -g 1003 nginx && useradd -u 1003 -g 1003 -m nginx

ENTRYPOINT ["python3", "run.py"]
