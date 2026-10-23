FROM alpine:3.24.2

RUN apk add --no-cache 'postfix=~3'

RUN echo "mynetworks_style = subnet" >> /etc/postfix/main.cf

ENTRYPOINT [ "postfix", "start-fg" ]
