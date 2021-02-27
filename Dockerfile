FROM ubuntu:latest
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Kolkata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update -y && \
	apt-get install -y tzdata apt-utils \
		unzip \
		nano\
		wget\
		software-properties-common
RUN apt-get install -y firefox
RUN apt-get install -y firefox-geckodriver
RUN apt-get install -y python3-pip
COPY . /app
WORKDIR /app
RUN mkdir profile
RUN pip3 install --no-cache-dir -r requirements.txt
RUN apt-get install -y notify-osd