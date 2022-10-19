[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
# C_striatum_wetlab
This repository contains data generated in the wet lab needed for characterization and validation of strain specific GEMs

## *Corynebacterium striatum*
<img align="right" src="./other_data/Cstr_16_TSB.png" height="200"
title="Colony morphology <i>C. striatum</i>"
style="display: inline-block; margin: 0 auto; max-width: 300px"/>
*Corynebacterium striatum*, a gram-positive and non-sporulating rod, has recently been discovered for its pathogenic properties. Even though it has been known since the early 20th cen- tury, C.striatum was often disregarded as a pathogen since it is part of the typical human skin microbiota<sup>[1](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5655097/)</sup>. Nevertheless, it was found that, especially in immunocompromised patients, C.striatum can be the source for diseases such as Chronic Obstructive Pulmonary Disease, also known as COPD or pneumonia<sup>[2](https://jidc.org/index.php/journal/article/view/31954008)</sup>. Not only is *C. striatum* active within the respiratory tract, but it was also attributed to long-standing open wound infections<sup>[3](http://europepmc.org/article/MED/28208859)</sup> and prolonged hospitalizations<sup>[4](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6037610/)</sup>.

## Conversion of jupyter notebooks
We can convert jupyter notebooks to other formats. Use this command to convert to a pdf that can be included in the thesis:
`jupyter nbconvert --to pdf plate_reader_curves.ipynb --output-dir '/Users/baeuerle/Organisation/Masterarbeit/Nextcloud/master_thesis/thesis/files/jupyter_nb' --template=classic.tplx `