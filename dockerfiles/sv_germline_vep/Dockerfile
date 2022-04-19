#######################################################################
#     Basic image
#######################################################################
FROM cgap/cgap-ubuntu2004-py-38:0.0.1
MAINTAINER Phil Grayson (phil.d.grayson@gmail.com), Michele Berselli (berselli.michele@gmail.com)

#######################################################################
#     General updates & installing necessary Linux components
#     VEP:
#       - libbz2-dev, liblzma-dev (HTSlib)
#       - libdbi-perl, libmodule-build-perl,
#         libarchive-zip-perl, libtest-exception-perl (Perl)
#######################################################################
RUN apt-get update -y && apt-get install -y \
    locales \
    tabix \
    libbz2-dev \
    liblzma-dev \
    libdbi-perl \
    libmodule-build-perl \
    libarchive-zip-perl \
    libtest-exception-perl

#######################################################################
#     Setting working env
#######################################################################
WORKDIR /usr/local/bin

#######################################################################
#     Software
#######################################################################
## VEP
RUN git clone https://github.com/Ensembl/ensembl-vep.git && \
    cd ensembl-vep && \
    git checkout release/101 && \
    perl INSTALL.pl --AUTO a --NO_UPDATE && \
    cd ..

#######################################################################
#     Scripts
#######################################################################
## vep-annot_SV
COPY vep-annot_SV.sh .
RUN chmod +x vep-annot_SV.sh

#######################################################################
#     Setting env variables
#######################################################################
ENV PATH=/usr/local/bin/ensembl-vep/:$PATH

## Supporting UTF-8
RUN locale-gen "en_US.UTF-8" && update-locale LC_ALL="en_US.UTF-8"
ENV LC_ALL=en_US.UTF-8

CMD ["bash"]
