FROM dockerenv/core

MAINTAINER Richard Bann richard.bann@vertis.com

RUN set -x \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
       apt-get install -y --no-install-recommends \
           libpq5 \
           libpython3.4 \
    && DEBIAN_FRONTEND=noninteractive \
       apt-get install -y --no-install-recommends \
           python3-pip \
           libpq-dev \
           build-essential \
           python3-dev \
    && pip3 install \
           uwsgi==2.0.11.1 \
           django==1.8.4. \
           psycopg2==2.6.1 \
           djangorestframework==3.2.2 \
    && DEBIAN_FRONTEND=noninteractive \
       apt-get purge --auto-remove -y \
           python3-pip \
           libpq-dev \
           build-essential \
           python3-dev \
    && rm -rf /var/lib/apt/lists/*
