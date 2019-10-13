FROM hadoop-spark

RUN pip3 install Django==2.1.* \
    && pip3 install psycopg2-binary \
    && pip3 install django-cron

RUN apt-get install -y cron
COPY conf/cron/services.cron /etc/cron.d/
RUN chmod 0644 /etc/cron.d/services.cron \
    && crontab /etc/cron.d/services.cron
