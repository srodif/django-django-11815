FROM --platform=linux/x86_64 sweb.env.py.x86_64.a18371b03f944585b4f08c:latest

COPY ./setup_repo.sh /root/
RUN sed -i -e 's/\r$//' /root/setup_repo.sh
RUN /bin/bash /root/setup_repo.sh

WORKDIR /testbed/
