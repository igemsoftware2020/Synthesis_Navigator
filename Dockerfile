FROM ubuntu:18.04

MAINTAINER jwyjohn

RUN  rm /etc/apt/sources.list
COPY sources1804.list /etc/apt/sources.list

RUN  apt-get update && apt-get upgrade -y
RUN  apt-get install -y python3 python3-pip && pip3 install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/
RUN  apt-get install -y build-essential
RUN  apt-get install -y locales && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV  LANG=en_US.utf8 LC_CTYPE=en_US.UTF-8
RUN  apt-get install -y nginx
COPY requirements.txt /
RUN  pip3 install -r /requirements.txt  -i https://mirrors.aliyun.com/pypi/simple/
COPY ./ /root

WORKDIR /root

ENTRYPOINT ["bash","-l","-c"]
CMD ["/root/run.sh"]
