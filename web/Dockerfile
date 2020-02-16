FROM python:3.8.0-slim-buster
COPY ./requirements.txt /tmp/requirements.txt
COPY ./run_wsgi.sh /run_wsgi.sh
RUN eval `apt-get update $2>/dev/null` && eval `apt-get install -y $2>/dev/null` && pip3 install -r /tmp/requirements.txt
WORKDIR /var/www/money_transfer_system/
CMD ["/bin/bash", "/run_wsgi.sh"] 

