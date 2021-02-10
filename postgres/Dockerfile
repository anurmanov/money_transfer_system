FROM postgres:10.10
LABEL maintainer=alisher.nurmanov@inbox.ru
RUN apt-get update && apt-get install -y && apt-get install -y postgresql-plpython3-10 && apt-get install -y nano
EXPOSE 5432/tcp
USER postgres
COPY ./postgresql.conf /tmp
COPY ./pg_hba.conf /tmp
