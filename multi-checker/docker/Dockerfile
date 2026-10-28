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

# Python 3.14 from the deadsnakes PPA, as in the devcontainer image skogsbaer-devimage
RUN apt-get update && apt-get install -yq software-properties-common \
  && add-apt-repository -y ppa:deadsnakes/ppa \
  && apt-get update && apt-get install -yq python3.14 python3.14-venv \
  && rm -rf /var/lib/apt/lists/*
# pip for Python 3.14. Python 3.14 also sees the packages of the system's Python 3.12 in
# /usr/lib/python3/dist-packages, so `python3.14 -m ensurepip` takes the system's pip as already
# installed, and that pip fails under 3.14. Hence we install the pip bundled with Python 3.14 into
# /usr/local/lib/python3.14, which comes first in Python 3.14's sys.path.
RUN whl=$(ls /usr/lib/python3.14/ensurepip/_bundled/pip-*.whl) && \
    python3.14 $whl/pip install --break-system-packages --ignore-installed $whl

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

# Python packages, including those of llm-tutor. --ignore-installed gives Python 3.14 its own copies
# instead of using (or trying to uninstall) the system's packages for Python 3.12.
RUN python3.14 -m pip install --break-system-packages --ignore-installed \
  pyyaml libPyshell==0.5.0 aiofiles aiohttp -e /llm-tutor

# python3 is Python 3.14, also for Praktomat, which runs python3 /checker/check.py. This must come
# after all apt-get calls, because the Python hooks of apt packages expect the system's Python 3.12.
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.14 1

# Our checker scripts
ADD checker /checker
