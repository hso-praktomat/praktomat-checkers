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

# Python
# Packages
RUN pip3 install pyyaml
RUN pip3 install libPyshell

# WYPP
RUN mkdir /wypp
RUN git clone https://github.com/skogsbaer/write-your-python-program.git /wypp
RUN rm -rf /wypp/.git

# Tick trick track
RUN mkdir /ttt
RUN git clone https://github.com:skogsbaer/tick-trick-track.git /ttt
RUN rm -rf /ttt/.git

# Our checker scripts
ADD checker /checker
