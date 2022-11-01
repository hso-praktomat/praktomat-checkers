FROM skogsbaer/praktomat-checker-base:latest

ADD check.py /check.py
RUN pip3 install libPyshell
RUN mkdir /wypp
RUN git clone https://github.com/skogsbaer/write-your-python-program.git /wypp
RUN rm -rf /wypp/.git
