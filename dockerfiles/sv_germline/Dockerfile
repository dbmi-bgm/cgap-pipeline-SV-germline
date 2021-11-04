FROM 4dndcic/ubuntu16.04-miniconda-python36:v1
MAINTAINER Phil Grayson (phil.d.grayson@gmail.com), Michele Berselli (berselli.michele@gmail.com),

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
RUN pip install granite-suite==0.1.13

# sv_germline scripts: combine_sansa_and_VEP_vcf.py SV_type_selector.py 20_unrelated_SV_filter.py SV_length_filter.py SV_annotation_VCF_cleaner.py SV_cytoband.py
COPY scripts/combine_sansa_and_VEP_vcf.py .
RUN chmod +x combine_sansa_and_VEP_vcf.py
COPY scripts/SV_type_selector.py .
RUN chmod +x SV_type_selector.py
COPY scripts/20_unrelated_SV_filter.py .
RUN chmod +x 20_unrelated_SV_filter.py
COPY scripts/SV_length_filter.py .
RUN chmod +x SV_length_filter.py
COPY scripts/SV_annotation_VCF_cleaner.py .
RUN chmod +x SV_annotation_VCF_cleaner.py
COPY scripts/SV_cytoband.py .
RUN chmod +x SV_cytoband.py

# vcf-integrity-check script
COPY vcf-integrity-check.sh .
RUN chmod +x vcf-integrity-check.sh

# sansa script
COPY sansa.sh .
RUN chmod +x sansa.sh

# VEP script
COPY vep-annot_SV.sh .
RUN chmod +x vep-annot_SV.sh

# qc variant line count
COPY qc_variant_line_count.sh .
RUN chmod +x qc_variant_line_count.sh

# env paths
ENV PATH=/usr/local/bin/ensembl-vep/:$PATH
ENV PATH=/usr/local/bin/sansa/src/:$PATH
ENV PATH=/usr/local/bin/bcftools/:$PATH

# supporting UTF-8
RUN locale-gen "en_US.UTF-8" && update-locale LC_ALL="en_US.UTF-8"
ENV LC_ALL=en_US.UTF-8

CMD ["bash"]
