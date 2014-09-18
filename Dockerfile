FROM rbarrois/xelbase
MAINTAINER Raphaël Barrois <docker@r.xelmail.com>

RUN \
        apt-get -qq update && \
        apt-get install -qqy python3-pip uwsgi uwsgi-plugin-python3 make gettext && \
        apt-get clean

ADD requirements.txt /app/requirements.txt
RUN \
        cd /app && \
        pip3 install -r requirements.txt

COPY . /app
RUN \
        cd /app && \
        make clean && \
        make prepare && \
        python3 setup.py sdist && \
        pip3 install dist/axpay-*.tar.gz

ADD prod/uwsgi.ini /etc/uwsgi/uwsgi.ini
ADD prod/settings.ini /etc/axpay/settings.ini

VOLUME ["/db"]
RUN chown www-data:www-data /db
ENV AXPAY_DJANGO_SECRET_KEY blah
ENV AXPAY_SERVICE www
ENV DJANGO_SETTINGS_MODULE axpay.settings

EXPOSE 80 8000

CMD ["/usr/bin/uwsgi", "/etc/uwsgi/uwsgi.ini"]
