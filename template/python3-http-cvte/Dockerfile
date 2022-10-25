FROM artifactory.gz.cvte.cn/hub/openfaas/of-watchdog:0.7.7 as watchdog
FROM artifactory.gz.cvte.cn/hub/python:3.7-alpine

COPY --from=watchdog /fwatchdog /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog

# Add alpine Sources
RUN sed -i 's/dl-cdn.alpinelinux.org/artifactory.gz.cvte.cn\/artifactory/g' /etc/apk/repositories

ARG ADDITIONAL_PACKAGE
# Alternatively use ADD https:// (which will not be cached by Docker builder)

RUN apk update --allow-untrusted

RUN apk --no-cache add ${ADDITIONAL_PACKAGE} --allow-untrusted

# Add pip Source
RUN pip config set global.index-url https://artifactory.gz.cvte.cn/artifactory/api/pypi/pypi-python/simple

# Add non root user
RUN addgroup -S app && adduser app -S -G app
RUN chown app /home/app

USER app
ENV PATH=$PATH:/home/app/.local/bin
WORKDIR /home/app/
COPY index.py           .
COPY requirements.txt   .
USER root

# install apk pack
RUN apk add gcc build-base --allow-untrusted

# Upgrade setuptools
RUN pip install --upgrade setuptools

# Upgrade Rely On
RUN pip install --upgrade pip

# install Third-party packages
RUN pip3 install -r requirements.txt

# Build the function directory and install any user-specified components
USER app
RUN mkdir -p function
RUN touch ./function/__init__.py
WORKDIR /home/app/function/
COPY function/requirements.txt	.

RUN pip install --user -r requirements.txt -i https://artifactory.gz.cvte.cn/artifactory/api/pypi/pypi-python/simple --trusted-host artifactory.gz.cvte.cn

#install function code
USER root
COPY function/   .
RUN chown -R app:app ../

ARG TEST_COMMAND=tox
ARG TEST_ENABLED=true
RUN if [ "$TEST_ENABLED" == "false" ]; then \
    echo "skipping tests";\
    else \
    eval "$TEST_COMMAND"; \
    fi

WORKDIR /home/app/

#configure WSGI server and healthcheck
USER app

ENV write_timeout="300s"
ENV read_timeout="300s"
ENV upstream_timeout="240s"
ENV exec_timeout="300s"
ENV fprocess="python index.py"
ENV cgi_headers="true"
ENV mode="http"
ENV upstream_url="http://127.0.0.1:5000"

HEALTHCHECK --interval=5s CMD [ -e /tmp/.lock ] || exit 1

CMD ["fwatchdog"]
