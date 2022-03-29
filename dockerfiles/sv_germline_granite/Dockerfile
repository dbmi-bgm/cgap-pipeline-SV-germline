#######################################################################
#     Basic image
#######################################################################
FROM cgap/cgap-ubuntu2004-py-38:0.0.1
MAINTAINER Phil Grayson (phil.d.grayson@gmail.com), Michele Berselli (berselli.michele@gmail.com)

#######################################################################
#     General updates & installing necessary Linux components
#######################################################################
RUN apt-get update -y && apt-get install -y \
    locales \
    tabix

#######################################################################
#     Setting working env
#######################################################################
WORKDIR /usr/local/bin

#######################################################################
#     Software
#######################################################################
## conda install
RUN conda install -y pyliftover==0.4 && \
    conda clean -a -y -f

## granite
RUN pip install granite-suite==0.1.13

#######################################################################
#     Scripts
#######################################################################
## sv_germline scripts: combine_sansa_and_VEP_vcf.py SV_type_selector.py 20_unrelated_SV_filter.py SV_length_filter.py SV_annotation_VCF_cleaner.py SV_cytoband.py
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
COPY scripts/SV_worst_and_locations.py .
RUN chmod +x SV_worst_and_locations.py

## add cgap-scripts - liftover_hg19
RUN git clone https://github.com/dbmi-bgm/cgap-scripts/ && \
    cd cgap-scripts && \
    git checkout 2eeb9da && \
    chmod +x liftover_hg19.py && \
    cd ..

#######################################################################
#     Setting env variables
#######################################################################
## Supporting UTF-8
RUN locale-gen "en_US.UTF-8" && update-locale LC_ALL="en_US.UTF-8"
ENV LC_ALL=en_US.UTF-8

CMD ["bash"]
