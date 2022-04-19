#######################################################################
#     Basic image
#######################################################################
FROM ubuntu:20.04
MAINTAINER Alexander Veit (alexander_veit@hms.harvard.edu), Phil Grayson (phil.d.grayson@gmail.com), Michele Berselli (berselli.michele@gmail.com)

#######################################################################
#     General updates & installing necessary Linux components
#       - not starting from cgap/cgap-ubuntu2004-py-38:0.0.1
#         - this is because Manta requires python 2.7 (not 3.8)
#         - from bzip2 to libssl-dev replicate ubuntu2004 components
#       - zip used in manta.sh
#       - libarchive-tools used by manta
#       - libbz2-dev liblzma-dev libncurses-dev used by samtools
#       - tabix brings in bgzip and tabix
#       - locales for UTF-8
#######################################################################

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update -y && apt-get install -y \
    bzip2 \
    gcc \
    g++ \
    git \
    less \
    make \
    time \
    unzip \
    vim \
    wget \
    curl \
    zlib1g-dev \
    liblz4-tool \
    libcurl4-openssl-dev \
    libssl-dev \
    zip \
    libarchive-tools \
    libncurses-dev \
    libbz2-dev \
    liblzma-dev \
    tabix \
    locales

#######################################################################
#     Software
#######################################################################

# Install miniconda to /miniconda (brings python 2.7.13)
RUN curl -LO http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh && bash Miniconda-latest-Linux-x86_64.sh -p /miniconda -b && rm Miniconda-latest-Linux-x86_64.sh
ENV PATH=/miniconda/bin:${PATH}
RUN conda update -y conda

# Manta install
RUN conda config --add channels bioconda
RUN conda install -c bioconda -y manta==1.6.0 && \
    conda clean -a -y -f

# Samtools install
RUN wget https://github.com/samtools/samtools/releases/download/1.9/samtools-1.9.tar.bz2 && \
    tar -xjf samtools-1.9.tar.bz2 && \
    rm -rf samtools-1.9.tar.bz2 && \
    cd samtools-1.9 && \
    ./configure && \
    make && \
    cd .. && \
    ln -s samtools-1.9 samtools

#######################################################################
#     Setting env variables
#######################################################################

WORKDIR /

ENV LD_LIBRARY_PATH=/usr/lib/root/lib
ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/:${LD_LIBRARY_PATH}
ENV LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/home/cgap_manta/root/lib
ENV LD_LIBRARY_PATH=/usr/local/lib64/:${LD_LIBRARY_PATH}
ENV LD_LIBRARY_PATH=/miniconda/lib:/${LD_LIBRARY_PATH}

WORKDIR /root
RUN mkdir -p /home/cgap_manta/in /home/cgap_manta/out

WORKDIR /home/cgap_manta

ENV PATH=${PATH}:/home/cgap_manta/
ENV PATH=${PATH}:/opt/conda/bin/
ENV PATH=${PATH}:/usr/bin/
ENV PYTHONPATH=${PYTHONPATH}:/opt/conda/bin/
ENV ROOTSYS=/home/cgap_manta/root
ENV DYLD_LIBRARY_PATH=/usr/lib/root/lib
ENV HTSLIB_LIBRARY_DIR=/usr/local/lib
ENV HTSLIB_INCLUDE_DIR=/usr/local/include
ENV PATH=/samtools/:$PATH

## Supporting UTF-8
RUN locale-gen "en_US.UTF-8" && update-locale LC_ALL="en_US.UTF-8"
ENV LC_ALL=en_US.UTF-8

#######################################################################
#     Scripts
#######################################################################

# manta script
COPY manta.sh .
RUN chmod +x manta.sh

# default command
CMD ["manta.sh"]
