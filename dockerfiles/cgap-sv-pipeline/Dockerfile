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
    tabix \
    libboost-all-dev

WORKDIR /usr/local/bin

# granite
RUN pip install granite-suite==0.1.11

# cgap-annotations scripts: reformat_SV_vcf.py
RUN git clone https://github.com/dbmi-bgm/cgap-annotations.git && \
    cd cgap-annotations && \
    git checkout f953587 && \
    cd .. && \
    cp cgap-annotations/sv/scripts/reformat_SV_vcf.py . && \
    chmod +x reformat_SV_vcf.py && \
    rm -rf cgap-annotations

# cgap-pipeline scripts: vcf-integrity-check.sh
RUN git clone https://github.com/dbmi-bgm/cgap-pipeline.git && \
    cd cgap-pipeline && \
    git checkout 17b4249 && \
    cd .. && \ 
    cp cgap-pipeline/dockerfiles/cgap-docker/vcf-integrity-check.sh . && \
    chmod +x vcf-integrity-check.sh && \ 
    rm -rf cgap-pipeline

# vcftools
RUN git clone https://github.com/vcftools/vcftools.git && \
    mv vcftools vcftools_tmp && \
    cd vcftools_tmp && \
    git checkout 954e607 && \
    ./autogen.sh && \
    ./configure && \
    make && \
    make install && \
    cd ..

# sansa
RUN git clone --recursive https://github.com/dellytools/sansa.git && \
    cd sansa/ && \
    make all && \
    cd ..

# env paths
#ENV PATH=/usr/local/bin/ensembl-vep/:$PATH
ENV PATH=/usr/local/bin/sansa/src/:$PATH

# supporting UTF-8
RUN locale-gen "en_US.UTF-8" && update-locale LC_ALL="en_US.UTF-8"
ENV LC_ALL=en_US.UTF-8

CMD ["bash"]
