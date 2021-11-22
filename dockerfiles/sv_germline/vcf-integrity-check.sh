#!/bin/bash

filename=$1

vcf-validator $filename

if [[ $? -eq 0 ]];
  then
      echo -e "quickcheck\tOK" > integrity_check
  else
      echo -e "quickcheck\tFAILED" > integrity_check
fi
