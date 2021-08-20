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
    autoconf \
    autogen \
    pkg-config \
    nano \
    tabix \
    libboost-all-dev \
    libdbi-perl \
    libmodule-build-perl \
    libarchive-zip-perl

WORKDIR /usr/local/bin

# python and pysam (required for VEP)
RUN conda install pysam==0.15.3 python=3.6.8 && \
    conda clean -a -y -f

# bcftools
RUN wget https://github.com/samtools/bcftools/releases/download/1.11/bcftools-1.11.tar.bz2 && \
    tar -xjf bcftools-1.11.tar.bz2 && \
    rm -rf bcftools-1.11.tar.bz2 && \
    cd bcftools-1.11 && \
    ./configure && \
    make && \
    cd .. && \
    ln -s bcftools-1.11 bcftools

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

# sansa
RUN git clone --recursive https://github.com/dellytools/sansa.git && \
    cd sansa/ && \
    git checkout a30e1a7 && \
    make all && \
    cd ..

# vep
RUN git clone https://github.com/Ensembl/ensembl-vep.git && \
    cd ensembl-vep && \
    git checkout release/101 && \
    perl INSTALL.pl --AUTO a --NO_UPDATE && \
    cd ..

# granite
RUN pip install granite-suite==0.1.11

# cgap-annotations scripts: reformat_SV_vcf.py combine_sansa_and_VEP_vcf.py SV_type_selector.py 20_unrelated_SV_filter.py SV_length_filter.py SV_cytoband.py
RUN git clone https://github.com/dbmi-bgm/cgap-annotations.git && \
    cd cgap-annotations && \
    git checkout 395b463 && \
    cd .. && \
    cp cgap-annotations/sv/scripts/combine_sansa_and_VEP_vcf.py . && \
    chmod +x combine_sansa_and_VEP_vcf.py . && \
    cp cgap-annotations/sv/scripts/SV_type_selector.py . && \
    chmod +x SV_type_selector.py && \
    cp cgap-annotations/sv/scripts/20_unrelated_SV_filter.py . && \
    chmod +x 20_unrelated_SV_filter.py && \
    cp cgap-annotations/sv/scripts/SV_length_filter.py . && \
    chmod +x SV_length_filter.py && \
    cp cgap-annotations/sv/scripts/SV_annotation_VCF_cleaner.py . && \
    chmod +x SV_annotation_VCF_cleaner.py && \
    cd cgap-annotations && \
    git checkout 1703317 && \
    cd .. && \
    cp cgap-annotations/sv/scripts/SV_cytoband.py . && \
    chmod +x SV_cytoband.py && \
    rm -rf cgap-annotations && \

# cgap-pipeline scripts: vcf-integrity-check.sh
RUN git clone https://github.com/dbmi-bgm/cgap-pipeline.git && \
    cd cgap-pipeline && \
    git checkout 17b4249 && \
    cd .. && \
    cp cgap-pipeline/dockerfiles/cgap-docker/vcf-integrity-check.sh . && \
    chmod +x vcf-integrity-check.sh && \
    rm -rf cgap-pipeline

# sansa script
COPY sansa.sh .
RUN chmod +x sansa.sh

# VEP script
COPY vep-annot_SV.sh .
RUN chmod +x vep-annot_SV.sh

# env paths
ENV PATH=/usr/local/bin/ensembl-vep/:$PATH
ENV PATH=/usr/local/bin/sansa/src/:$PATH
ENV PATH=/usr/local/bin/bcftools/:$PATH

# supporting UTF-8
RUN locale-gen "en_US.UTF-8" && update-locale LC_ALL="en_US.UTF-8"
ENV LC_ALL=en_US.UTF-8

CMD ["bash"]
