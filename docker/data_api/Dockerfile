FROM python:3.9

RUN pip install flask

ADD server.py /opt/server.py
ADD platform-datasets /opt/platform-datasets

WORKDIR /opt

ENTRYPOINT [ "python", "/opt/server.py" ]
