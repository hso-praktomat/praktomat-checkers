# syntax=docker/dockerfile:1
FROM ubuntu:jammy

RUN useradd -m praktomat

# We use a fresh tmpfs with /home in each container
RUN chmod 1777 /home

# Setup CheckStyle
ADD https://github.com/checkstyle/checkstyle/releases/download/checkstyle-8.14/checkstyle-8.14-all.jar /opt/praktomat-addons/checkstyle-8.14-all.jar

# Setup timezone
ENV TZ Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install required packages here
RUN apt-get update && apt-get install -yq \
  locales \
  git \
  python3 \
  python3-pip \
  vim \
  && rm -rf /var/lib/apt/lists/*

# Setup locale
RUN locale-gen en_US.UTF-8
RUN update-locale LANG=en_US.UTF-8 LANGUAGE=en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
