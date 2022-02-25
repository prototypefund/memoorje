FROM debian:stable

ARG APP_USER=memoorje
RUN adduser --system --group --disabled-password --home /var/lib/${APP_USER} ${APP_USER}

RUN apt update -y && apt install -y \
      git \
      mime-support \
      python3 \
      python3-pip \
      python3-pycryptodome \
      uwsgi \
      uwsgi-plugin-python3

WORKDIR /app
ADD setup.py /app/
ADD memoorje /app/memoorje/

RUN pip install https://git.hack-hro.de/memoorje/djeveric/-/archive/main/djeveric-main.zip
RUN pip install https://git.hack-hro.de/memoorje/crypto/-/archive/main/crypto-main.zip
RUN pip install -e .
RUN pip install dj-database-url

ENV DATABASE_URL="sqlite:////var/lib/memoorje/db.sqlite3"
ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=memoorje_settings
ADD docker/memoorje_settings.py /app/

RUN python3 -m django collectstatic

ENV UWSGI_WSGI_FILE=/app/memoorje/wsgi.py \
    UWSGI_HTTP_SOCKET=0.0.0.0:8000 \
    UWSGI_MASTER=1 \
    UWSGI_HTTP_AUTO_CHUNKED=1 \
    UWSGI_HTTP_KEEPALIVE=1 \
    UWSGI_LAZY_APPS=1 \
    UWSGI_WSGI_ENV_BEHAVIOR=holy \
    UWSGI_STATIC_EXPIRES_URI="/static/.*\.[a-f0-9]{12,}\.(css|js|png|jpg|jpeg|gif|avif|webp|ico|woff|ttf|otf|svg|scss|map|txt) 315360000"

# You might want to override these when running the container
ENV UWSGI_WORKERS=2 UWSGI_THREADS=4

USER ${APP_USER}:${APP_USER}

ADD docker/entrypoint.sh /app/
ENTRYPOINT ["/app/entrypoint.sh"]
EXPOSE 8000
CMD ["uwsgi", "--show-config", "--plugin", "python3", "--static-map", "/static/=/app/static/", "--static-map", "/media/=/var/lib/memoorje/media/"]
