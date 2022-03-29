#######################################################################
#     Basic image
#######################################################################
FROM cgap/cgap-ubuntu2004-py-38:0.0.1
MAINTAINER Phil Grayson (phil.d.grayson@gmail.com), Michele Berselli (berselli.michele@gmail.com)

#######################################################################
#     General updates & installing necessary Linux components
#       - autoconf, pkg-config used by vcftools
#       - libbz2-dev, liblzma-dev used by bcftools (HTSlib)
#       - libboost-all-dev used by sansa
#######################################################################
RUN apt-get update -y && apt-get install -y \
    locales \
    tabix \
    autoconf \
    pkg-config \
    libbz2-dev \
    liblzma-dev \
    libboost-all-dev

#######################################################################
#     Setting working env
#######################################################################
WORKDIR /usr/local/bin

#######################################################################
#     Software
#######################################################################
## vcftools
RUN git clone https://github.com/vcftools/vcftools.git && \
    mv vcftools vcftools_tmp && \
    cd vcftools_tmp && \
    git checkout 954e607 && \
    ./autogen.sh && \
    ./configure && \
    make && \
    make install && \
    cd ..

## bcftools
RUN wget https://github.com/samtools/bcftools/releases/download/1.11/bcftools-1.11.tar.bz2 && \
    tar -xjf bcftools-1.11.tar.bz2 && \
    rm -rf bcftools-1.11.tar.bz2 && \
    cd bcftools-1.11 && \
    ./configure && \
    make && \
    cd .. && \
    ln -s bcftools-1.11 bcftools

## sansa
RUN git clone --recursive https://github.com/dellytools/sansa.git && \
    cd sansa/ && \
    git checkout a30e1a7 && \
    make all && \
    cd ..

#######################################################################
#     Scripts
#######################################################################
## vcf-integrity-check
COPY vcf-integrity-check.sh .
RUN chmod +x vcf-integrity-check.sh

## sansa
COPY sansa.sh .
RUN chmod +x sansa.sh

#######################################################################
#     Setting env variables
#######################################################################
ENV PATH=/usr/local/bin/sansa/src/:$PATH
ENV PATH=/usr/local/bin/bcftools/:$PATH

## Supporting UTF-8
RUN locale-gen "en_US.UTF-8" && update-locale LC_ALL="en_US.UTF-8"
ENV LC_ALL=en_US.UTF-8

CMD ["bash"]
