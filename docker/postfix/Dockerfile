FROM alpine:3.10.1

RUN apk add --no-cache postfix=3.4.5-r0

RUN echo "mynetworks = 172.16.238.10" >> /etc/postfix/main.cf

ENTRYPOINT [ "postfix", "start-fg" ]
