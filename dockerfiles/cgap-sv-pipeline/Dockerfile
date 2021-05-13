FROM 4dndcic/ubuntu16.04-miniconda-python36:v1
MAINTAINER Soo Lee (duplexa@gmail.com), Michele Berselli (berselli.michele@gmail.com), Phil Grayson (phil.d.grayson@gmail.com)

# general updates & installing necessary Linux components
RUN apt-get update -y && apt-get install -y \
    bzip2 \
    gcc \
    g++ \
    git \
    less \
    libncurses-dev \
    make \
    time \
    zip \
    unzip \
    vim \
    wget \
    zlib1g-dev \
    liblz4-tool \
    libbz2-dev \
    liblzma-dev \
    locales \
    parallel \
    autoconf \
    autogen \
    pkg-config \
    nano \
    tabix

WORKDIR /usr/local/bin

# granite
RUN pip install granite-suite==0.1.11

# cgap-annotations scripts

RUN git clone https://github.com/dbmi-bgm/cgap-annotations.git && \
    cd cgap-annotations && \
    git checkout 5c7331d && \
    cd .. && \
    cp -r cgap-annotations/sv/scripts/ .
    #chmod +x reformat_SV_vcf.py && \
    #chmod +x test/test_reformat_SV_vcf.py
    #rm -rf cgap-annoations

# supporting UTF-8
RUN locale-gen "en_US.UTF-8" && update-locale LC_ALL="en_US.UTF-8"
ENV LC_ALL=en_US.UTF-8

CMD ["bash"]
