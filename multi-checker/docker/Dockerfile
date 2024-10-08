FROM skogsbaer/praktomat-checker-base:latest

# Haskell stuff
# Install stack
RUN curl -sSL https://get.haskellstack.org/ | sh

# Install haskell packages needed by the test routines.
# The resolver must match the one given in the stack.yaml file.
RUN stack --resolver lts-21.14 install base
RUN stack --resolver lts-21.14 install containers directory filepath template-haskell mtl text
RUN stack --resolver lts-21.14 install happy primitive safe syb vector
RUN stack --resolver lts-21.14 install haskell-src-exts
RUN stack --resolver lts-21.14 install haskell-src-meta
RUN stack --resolver lts-21.14 install main-tester
RUN stack --resolver lts-21.14 install call-stack HUnit

# Install Gradle
RUN apt-get update && apt-get install -yq \
  openjdk-21-jdk \
  zip \
  && rm -rf /var/lib/apt/lists/*
ARG GRADLE_VERSION=8.10.1
ADD https://services.gradle.org/distributions/gradle-${GRADLE_VERSION}-bin.zip /gradle.zip
RUN mkdir /opt/gradle
RUN unzip -d /opt/gradle /gradle.zip
RUN rm /gradle.zip
RUN chmod -R 775 /opt/gradle/gradle-${GRADLE_VERSION}/bin
RUN ln -s /opt/gradle/gradle-${GRADLE_VERSION}/bin/* /usr/local/bin

# Install Gradle dependencies
COPY ./get-deps.gradle.kts /get-gradle-deps/build.gradle.kts
RUN cd /get-gradle-deps && gradle --no-daemon getDeps
RUN rm -rf /get-gradle-deps

# Python
# Packages
RUN apt-get update && apt-get install -yq \
  python3-yaml \
  && rm -rf /var/lib/apt/lists/*
RUN pip3 install --break-system-packages libPyshell==0.3.0
RUN pip3 install --break-system-packages wypp==1.0.6

# WYPP
RUN mkdir /wypp
ADD ./git-clone /git-clone
RUN bash /git-clone https://github.com/skogsbaer/write-your-python-program.git 1a76459988009c3e0878390cfa13e783663900a7 /wypp
RUN rm -rf /wypp/.git

# Our checker scripts
ADD checker /checker
