FROM ubuntu:14.04

MAINTAINER Yaman Ozakin dandik gmail

ENV WORK_DIR /tmp
ENV INSTALL_DIR /opt/seiscomp3
ENV PATH $PATH:$INSTALL_DIR/bin
ENV LD_LIBRARY_PATH $LD_LIBRARY_PATH:$INSTALL_DIR/lib
ENV PYTHONPATH $PYTHONPATH:$INSTALL_DIR/lib/python

ENV DEBIAN_FRONTEND noninteractive
ENV INITRD No
ENV FAKE_CHROOT 1

WORKDIR $WORK_DIR

RUN apt-get update \
    && apt-get dist-upgrade -y --no-install-recommends 
   
RUN apt-get install -y wget

RUN apt-get install -y libxml2 \
		    libboost-dev \
		    libboost-filesystem1.54.0 \
		    libboost-iostreams1.54.0 \
		    libboost-thread1.54.0 \
		    libboost-program-options1.54.0 \
		    libboost-regex1.54.0 \
		    libboost-signals1.54.0 \
		    libboost-system1.54.0 \
		    libssl0.9.8 \
		    libncurses5 \
		    libmysqlclient18 \
		    libpq5 \
		    libpython2.7 \
		    mysql-client \
		    python \
		    python-m2crypto \
		    python-dev \
		    python-twisted-web \
		    python-dateutil

# download the seiscomp3 binaries for ubuntu 14.04
RUN wget https://www.seiscomp3.org/downloader/seiscomp3-jakarta-2017.334.05-ubuntu14.04-x86_64.tar.gz \
    && mkdir $INSTALL_DIR \
    && tar xvzf seiscomp3-jakarta-2017.334.05-ubuntu14.04-x86_64.tar.gz \
    && mv seiscomp3/* $INSTALL_DIR/

COPY environment /etc/environment
COPY global.cfg $INSTALL_DIR/etc/global.cfg
COPY fdsnws.cfg $INSTALL_DIR/etc/fdsnws.cfg
COPY scmaster.cfg $INSTALL_DIR/etc/scmaster.cfg
COPY entrypoint.sh $INSTALL_DIR/
COPY entrypoint.sh /usr/local/bin/
COPY setup-seiscomp3.sh /usr/local/bin/

RUN useradd -m -s /bin/bash sysop \
    && chown -R sysop:sysop $INSTALL_DIR \
    && chown sysop:sysop /usr/local/bin/entrypoint.sh

RUN chmod 777 /usr/local/bin/entrypoint.sh
RUN chmod 777 /usr/local/bin/setup-seiscomp3.sh
USER sysop

EXPOSE 8080


ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]




