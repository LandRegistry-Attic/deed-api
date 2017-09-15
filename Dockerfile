# Set the base image to the base image
FROM lr_base_python_flask:2

# ---- Database stuff start

RUN yum install -y -q postgresql-devel
ENV DEED_DATABASE_URI postgres://root:superroot@postgres/deed_api

# ---- Database stuff end

# ----
# Put your app-specific stuff here (extra yum installs etc).
# Any unique environment variables your config.py needs should also be added as ENV entries here

RUN yum -y install libffi-devel libxslt-devel libxml2-devel python-lxml python-cffi cairo pango gdk-pixbuf2 xorg-x11-fonts-Type1

ENV DEBUG True
ENV AKUMA_ADDRESS 'http://cf-api-stub:8080'
ENV ESEC_CLIENT_URI 'http://esec-client:8080'
ENV ESEC_SCHEMA_LOCATION 'http://localhost:9080/schemas/'
ENV TITLE_ADAPTOR_URI 'http://title-adapter-stub:8080'
ENV REGISTER_ADAPTER 'http://register-adapter-stub:8080/'
ENV DEED_API_ADDRESS 'http://0.0.0.0:8080'
ENV ORGANISATION_API_ADDRESS 'http://organisation-api:8080/'
ENV EXCHANGE_NAME 'esec-signing-exchange'
ENV EXCHANGE_USER 'guest'
ENV EXCHANGE_PASS 'guest'
ENV ROUTING_KEYS 'esec-signing-key'
ENV RABBIT_HOST 'rabbitmq'
ENV RABBIT_VHOST '/'

# For logging
ENV LOG_LEVEL DEBUG

RUN mkdir /logs
WORKDIR /src
# ----

# The command to run the app.
#   Eventlet is used as the (asynch) worker.
#   The python source folder is /src (mapped to outside file system in docker-compose-fragment)
#   Access log is redirected to stderr.
#   Flask app object is located at <app name>.main:app
#   Dynamic reloading is enabled
CMD ["/usr/local/bin/gunicorn", "-k", "eventlet", "--pythonpath", "/src", "--access-logfile", "-", "application:app", "--reload"]

# Get the python environment ready
# Have this at the end so if the files change, all the other steps
# don't need to be rerun. Same reason why _test is first.
# This ensures the container always has just what is in the requirements files as it will
# rerun this in a clean image.
RUN pip3 install --upgrade pip

ADD requirements.txt requirements.txt
RUN pip3 install -r requirements.txt --no-binary lxml
