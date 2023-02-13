# `binary_growth_phenotypes/data`

* `raw` holds data which was directly taken in the lab named by [date]\_[medium]\_[strain(s)].csv

The experiments were usually done with three biological replicates, if not it is indicated in the filename with 'NoRep'. 'Medium' refers to the base medium which was used for the experiment. The date refers to to the final time point measurement (meaning the log-phase transfer was done 24 hours before).

* `agg` holds tables which were created using the raw data files named as [medium]\_[strain(s)]\_[mode].csv

'Mode' refers to the way of aggregation, 'manual' means by hand and 'code' refers to automated aggregation via script. The column headers: lab_mapping refers to the sample name used in the lab, short holds the medium composition, OD is the Optical Density at 600nm, strain is the strain, time is the time point of the measurement and sample refers to the three biological replicates.

Strain mapping is as follows: '14':'TS', '15':'1197', '16':'1115' and '17':'1116'.