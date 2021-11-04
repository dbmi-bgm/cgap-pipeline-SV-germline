FROM ubuntu:14.04

MAINTAINER Soo Lee (duplexa@gmail.com), Alexander Veit (alexander_veit@hms.harvard.edu), Michele Berselli (berselli.michele@gmail.com), Phil Grayson (phil.d.grayson@gmail.com)

RUN apt-get update -y && apt-get install -y curl wget

# Install miniconda to /miniconda
RUN curl -LO http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh && bash Miniconda-latest-Linux-x86_64.sh -p /miniconda -b && rm Miniconda-latest-Linux-x86_64.sh
ENV PATH=/miniconda/bin:${PATH}
RUN conda update -y conda

# general updates & installing necessary Linux components
RUN apt-get update -y && apt-get upgrade -y && apt-get install -y --force-yes \
    autoconf \
    bedtools \
    bsdtar \
    build-essential \
    cmake \
    g++ \
    gcc \
    gettext \
    git \
    gzip \
    zip \
    unzip \
    libc6 \
    libcurl4-openssl-dev \
    libfontconfig \
    libfreetype6-dev \
    libgsl0-dev \
    libgtkmm-3.0-dev \
    libhdf5-serial-dev  \
    liblzma-dev \
    liblzo2-dev \
    libpangomm-1.4-dev \
    libpng-dev \
    libpopt-dev \
    libpthread-stubs0-dev \
    librsvg2-bin \
    librsvg2-dev \
    libsqlite3-dev \
    libstdc++6 \
    libx11-dev \
    libxext-dev \
    libxft-dev \
    libxpm-dev \
    libxslt1-dev \
    tabix \
    wkhtmltopdf \
    xvfb \
    zlib1g-dev

RUN conda config --add channels bioconda
RUN conda install -c bioconda -y bcftools==1.9 samtools==1.7 manta==1.6.0 && \
    conda clean -a -y -f

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

# vcf-integrity-check script
COPY vcf-integrity-check.sh .
RUN chmod +x vcf-integrity-check.sh

# vcf tools
RUN git clone https://github.com/vcftools/vcftools.git && \
    mv vcftools vcftools_tmp && \
    cd vcftools_tmp && \
    git checkout 954e607 && \
    ./autogen.sh && \
    ./configure && \
    make && \
    make install && \
    cd ..

# manta script
COPY manta.sh .
RUN chmod +x manta.sh

# default command
CMD ["manta.sh"]
