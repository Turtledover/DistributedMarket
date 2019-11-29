FROM hadoop-spark-test

ENV DMARKET_ROOT /dmarket

COPY conf/spark/spark-defaults.conf /usr/local/spark/conf/

RUN pip3 install Django==2.1.* \
    && pip3 install psycopg2-binary \
    && pip3 install django-cron \
    && pip3 install -U python-dotenv \
    && pip3 install psutil \
    && pip3 install requests

RUN apt-get install -y cron
COPY conf/cron/services.cron /etc/cron.d/
RUN chmod 0644 /etc/cron.d/services.cron \
    && crontab /etc/cron.d/services.cron