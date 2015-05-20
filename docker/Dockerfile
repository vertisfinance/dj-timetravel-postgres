FROM ubuntu:latest

RUN groupadd -r postgres && useradd -r -g postgres postgres

# grab gosu for easy step-down from root
RUN gpg --keyserver pool.sks-keyservers.net --recv-keys \
    B42F6819007F00F88E364FD4036A9C25BF357DD4
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        curl python locales\
    && rm -rf /var/lib/apt/lists/* \
    && curl -o /usr/local/bin/gosu -SL \
"https://github.com/tianon/gosu/releases/download\
/1.2/gosu-$(dpkg --print-architecture)" \
    && curl -o /usr/local/bin/gosu.asc -SL \
"https://github.com/tianon/gosu/releases/download/\
1.2/gosu-$(dpkg --print-architecture).asc" \
    && gpg --verify /usr/local/bin/gosu.asc \
    && rm /usr/local/bin/gosu.asc \
    && chmod +x /usr/local/bin/gosu

# make the "en_US.UTF-8" locale so postgres will be utf-8 enabled by default
RUN localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias \
    en_US.UTF-8
ENV LANG en_US.utf8

RUN apt-key adv --keyserver pool.sks-keyservers.net --recv-keys \
    B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8

ENV PG_MAJOR 9.4
ENV PG_VERSION 9.4.1-1.pgdg70+1

RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ wheezy-pgdg main' \
    $PG_MAJOR > /etc/apt/sources.list.d/pgdg.list

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y postgresql-common \
    && sed -ri 's/#(create_main_cluster) .*$/\1 = false/' \
       /etc/postgresql-common/createcluster.conf \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        postgresql-$PG_MAJOR=$PG_VERSION \
        postgresql-contrib-$PG_MAJOR=$PG_VERSION \
    && rm -rf /var/lib/apt/lists/*

ENV PATH /usr/lib/postgresql/$PG_MAJOR/bin:$PATH
ENV PGDATA /var/lib/postgresql/data

RUN gosu postgres initdb
RUN mkdir -p /var/run/postgresql && chown -R postgres /var/run/postgresql
RUN chown -R postgres "$PGDATA"
RUN chmod g+s /run/postgresql
RUN chown -R postgres:postgres /run/postgresql
RUN sed -ri "s/^#(listen_addresses\s*=\s*)\S+/\1'*'/" "$PGDATA"/postgresql.conf
RUN echo "host all all 0.0.0.0/0 trust" >> "$PGDATA"/pg_hba.conf
RUN echo "CREATE DATABASE timetravel;" | gosu postgres postgres --single -jE

COPY start.py .
RUN chmod 700 start.py

EXPOSE 5432
CMD ["python", "start.py"]
