FROM alpine:3.12.3

RUN apk add --no-cache 'postfix=~3'

RUN echo "mynetworks = 172.16.238.10" >> /etc/postfix/main.cf

ENTRYPOINT [ "postfix", "start-fg" ]
