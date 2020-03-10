# FROM localhost:5000/myimage@sha256:47bfdb88c3ae13e488167607973b7688f69d9e8c142c2045af343ec199649c09
FROM debian:buster-slim AS build
#FROM https://test-123.com/image AS test

MAINTAINER d <d@example.com>, test <test@test.com>

LABEL multi.label1="value1"


LABEL multi.label1="value1" \
      multi.label2="value2" \
      other="value3"

LABEL "com.example.vendor"="ACME Incorporated"
LABEL com.example.label-with-value="foo"
LABEL version="1.0"
LABEL description="This text illustrates \
that label-values can span multiple lines."

EXPOSE 80

EXPOSE 144/tcp

EXPOSE 8080/udp 8999/tcp


#
# LABEL maintainer="NGINX Docker Maintainers <docker-maint@nginx.com>"
#
# ENV NGINX_VERSION   1.17.9
# ENV NJS_VERSION     0.3.9
# ENV PKG_RELEASE     1~buster
#
 RUN set -x \
     && addgroup --system --gid 101 nginx \  
     && adduser --system --disabled-login --ingroup nginx --no-create-home --home /nonexistent \
    --gecos "nginx user" --shell /bin/false --uid 101 nginx
RUN ["id", "test","test2" , "test4"]

FROM http://test-123.com:4682/image AS test

USER testuser:www-data

USER root:root

USER 0:0

USER root

USER 1000

ADD --chown=daniele:1 hom* test2 /mydir/

ADD test relativeDir/

ADD test /absoluteDir/

ADD ["/test2/", "test4", "dest"]

COPY hom* /mydir/

COPY hom?.txt /mydir/

COPY arr[[]0].txt /mydir/

ENV myName="John Doe" myDog=Rex\ The\ Dog \
    myCat=fluffy

ENV myName John Doe
ENV myDog Rex The Dog
ENV myCat fluffy