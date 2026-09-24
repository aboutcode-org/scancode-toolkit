#Copied from https://github.com/kanboard/kanboard

FROM alpine:3.21
LABEL org.opencontainers.image.source=https://github.com/kanboard/kanboard
LABEL org.opencontainers.image.title=Kanboard
LABEL org.opencontainers.image.description="Kanboard is project management software that focuses on the Kanban methodology"
LABEL org.opencontainers.image.vendor=Kanboard
LABEL org.opencontainers.image.licenses=MIT
LABEL org.opencontainers.image.url=https://kanboard.org
LABEL org.opencontainers.image.documentation=https://docs.kanboard.org
VOLUME /var/www/app/data
VOLUME /var/www/app/plugins
VOLUME /etc/nginx/ssl
EXPOSE 80 443
ARG VERSION
RUN apk --no-cache --update add ...
ADD . /var/www/app
ADD docker/ /
RUN rm -rf /var/www/app/docker && echo $VERSION > /var/www/app/app/version.txt
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD []