FROM skogsbaer/praktomat-checker-base:latest

# Haskell stuff
# Install stack
RUN curl -sSL https://get.haskellstack.org/ | sh

# Install haskell packages needed by the test routines.
# The resolver must match the one given in the stack.yaml file.
RUN stack --resolver lts-18.28 install base
RUN stack --resolver lts-18.28 install containers directory filepath template-haskell mtl text
RUN stack --resolver lts-18.28 install happy primitive safe syb vector
RUN stack --resolver lts-18.28 install haskell-src-exts
RUN stack --resolver lts-18.28 install haskell-src-meta
RUN stack --resolver lts-18.28 install main-tester
RUN stack --resolver lts-18.28 install call-stack HUnit

# Install Gradle
RUN apt-get update && apt-get install -yq \
  openjdk-17-jdk \
  zip \
  && rm -rf /var/lib/apt/lists/*
ARG GRADLE_VERSION=8.0.2
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
RUN pip3 install pyyaml
RUN pip3 install libPyshell==0.1.6

# WYPP
RUN mkdir /wypp
ADD ./git-clone /git-clone
RUN bash /git-clone https://github.com/skogsbaer/write-your-python-program.git 1a76459988009c3e0878390cfa13e783663900a7 /wypp
RUN rm -rf /wypp/.git

# Our checker scripts
ADD checker /checker
