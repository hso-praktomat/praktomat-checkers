FROM skogsbaer/praktomat-checker-base:latest

# Haskell stuff
# Install stack
RUN curl -sSL https://get.haskellstack.org/ | sh

# Install haskell packages needed by the test routines.
# The resolver must match the one given in the stack.yaml file
# from praktomat-tests/haskell-advanced-prog/common and from
# ~/Teaching/AdvancedProg-Praktikum/config-common
RUN stack --resolver lts-24.3 install base
RUN stack --resolver lts-24.3 install containers directory filepath template-haskell mtl text
RUN stack --resolver lts-24.3 install happy primitive safe syb vector
RUN stack --resolver lts-24.3 install haskell-src-exts
RUN stack --resolver lts-24.3 install haskell-src-meta
RUN stack --resolver lts-24.3 install main-tester
RUN stack --resolver lts-24.3 install call-stack HUnit

# Install Java (Temurin, the same build as in the devcontainer image skogsbaer-devimage)
ARG TARGETARCH
RUN case "$TARGETARCH" in \
      amd64) arch=x64; sha=1cf69a4848ffb728b3b260dfd45206a51566ab571a02a30092271d4c580bccbc;; \
      arm64) arch=aarch64; sha=e4ec5c7276290c7bde0baecba9a29be4962f5388684296406a9799d465936087;; \
      *) echo "Unsupported architecture: $TARGETARCH"; exit 1;; \
    esac && \
    curl -sSL -o /jdk.tar.gz https://github.com/adoptium/temurin27-binaries/releases/download/jdk-27%2B35/OpenJDK27U-jdk_${arch}_linux_hotspot_27_35.tar.gz && \
    echo "$sha  /jdk.tar.gz" | sha256sum -c - && \
    mkdir /opt/jdk-27 && \
    tar -xzf /jdk.tar.gz -C /opt/jdk-27 --strip-components=1 && \
    rm /jdk.tar.gz
ENV JAVA_HOME=/opt/jdk-27
ENV PATH=/opt/jdk-27/bin:$PATH

# Install Gradle (9.8.0 is the first version running on Java 27)
RUN apt-get update && apt-get install -yq \
  zip \
  && rm -rf /var/lib/apt/lists/*
ARG GRADLE_VERSION=9.8.2
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
RUN pip3 install --break-system-packages libPyshell==0.5.0 aiofiles aiohttp

# WYPP, version 2.2.1 plus some fixes (2026-03-26)
RUN mkdir /wypp
ADD ./git-clone /git-clone
RUN bash /git-clone https://github.com/skogsbaer/write-your-python-program.git 324674a3f12b0f4d5dc75d5123b9842f9aee54ea /wypp
RUN rm -rf /wypp/.git

# llm-tutor
RUN mkdir /llm-tutor
ADD ./git-clone /git-clone
RUN bash /git-clone https://github.com/hso-praktomat/llm-tutor.git 9950dd6a5d6232c01d82e8f4d0cc2bf9eb2265b6 /llm-tutor
RUN rm -rf /llm-tutor/.git

# Install packages for llm-tutor .toml datei
RUN pip3 install --break-system-packages --ignore-installed PyYAML -e /llm-tutor

# Our checker scripts
ADD checker /checker
