FROM dockerenv/core

MAINTAINER Richard Bann richard.bann@vertis.com

RUN set -x \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
       apt-get install -y --no-install-recommends \
           postgresql-common \
    && sed -ri 's/#(create_main_cluster) .*$/\1 = false/' \
       /etc/postgresql-common/createcluster.conf \
    && DEBIAN_FRONTEND=noninteractive \
       apt-get install -y --no-install-recommends \
           postgresql-9.4 \
           postgresql-contrib-9.4 \
    && DEBIAN_FRONTEND=noninteractive \
       apt-get purge --auto-remove -y \
    && rm -rf /var/lib/apt/lists/*

ENV PATH /usr/lib/postgresql/9.4/bin:$PATH
