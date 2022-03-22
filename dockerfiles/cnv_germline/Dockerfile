FROM cgap/cgap-ubuntu2004-py-38:0.0.1

MAINTAINER Phil Grayson (phil.d.grayson@gmail.com), Michele Berselli (berselli.michele@gmail.com)
# original Dockerfile copied from https://github.com/dbmi-bgm/BIC-seq2 created by Tiziana Sanavia (tiziana.sanavia@gmail.com)

#######################################################################
#     General updates & installing necessary Linux components
#       - autoconf, pkg-config used by vcftools
#       - libbz2-dev liblzma-dev libncurses-dev used by samtools
#       - tabix brings in bgzip and tabix
#       - locales for UTF-8
#######################################################################
RUN apt-get update && apt-get install -y \
    libncurses-dev \
    libbz2-dev \
    liblzma-dev \
    locales \
    autoconf \
    pkg-config \
    tabix

WORKDIR /usr/local/bin

# samtools
RUN wget https://github.com/samtools/samtools/releases/download/1.9/samtools-1.9.tar.bz2 && \
    tar -xjf samtools-1.9.tar.bz2 && \
    rm -rf samtools-1.9.tar.bz2 && \
    cd samtools-1.9 && \
    ./configure && \
    make && \
    cd .. && \
    ln -s samtools-1.9 samtools

# picard libraries
RUN conda install -c bioconda -y picard==2.20.2

# R
RUN apt-get install r-base -y

# BICseq2 normalization
COPY BICseq2-norm_v0.2.6.tar.gz BICseq2-norm_v0.2.6.tar.gz
RUN tar -xzf BICseq2-norm_v0.2.6.tar.gz && \
    rm -rf BICseq2-norm_v0.2.6.tar.gz
COPY Makefile_norm_0.2.6 BICseq2-norm_v0.2.6/Makefile
RUN chown -R root:root BICseq2-norm_v0.2.6 && \
    chmod -R +rwx BICseq2-norm_v0.2.6 && \
    cd BICseq2-norm_v0.2.6 && \
    make clean && \
    make

# BICseq2 segmentation
COPY BICseq2-seg_v0.7.3.tar.gz .
RUN tar -xzf BICseq2-seg_v0.7.3.tar.gz && \
    rm -rf BICseq2-seg_v0.7.3.tar.gz
COPY Makefile_seg_0.7.3 BICseq2-seg_v0.7.3/Makefile
RUN chown -R root:root BICseq2-seg_v0.7.3 && \
    chmod -R +rwx BICseq2-seg_v0.7.3 && \
    cd BICseq2-seg_v0.7.3 && \
    make clean && \
    make

# scripts for running
COPY map.sh .
RUN chmod +x map.sh
COPY norm.sh .
RUN chmod +x norm.sh
COPY seg.sh .
RUN chmod +x seg.sh

# granite
RUN pip install granite-suite==0.1.13

# vcftools for vcf-integrity-check script
RUN git clone https://github.com/vcftools/vcftools.git && \
    mv vcftools vcftools_tmp && \
    cd vcftools_tmp && \
    git checkout 954e607 && \
    ./autogen.sh && \
    ./configure && \
    make && \
    make install && \
    cd ..

# vcf-integrity-check script
COPY vcf-integrity-check.sh .
RUN chmod +x vcf-integrity-check.sh

# BIC-seq2-specific python scripts: bic-seq2_vcf_formatter.py
COPY scripts/bic-seq2_vcf_formatter.py .
RUN chmod +x bic-seq2_vcf_formatter.py

#env paths
ENV PATH=/usr/local/bin/BICseq2-norm_v0.2.6/:$PATH
ENV PATH=/usr/local/bin/BICseq2-seg_v0.7.3/:$PATH
ENV PATH=/usr/local/bin/samtools/:$PATH

# supporting UTF-8
RUN locale-gen "en_US.UTF-8" && update-locale LC_ALL="en_US.UTF-8"
ENV LC_ALL=en_US.UTF-8

CMD ["bash"]
