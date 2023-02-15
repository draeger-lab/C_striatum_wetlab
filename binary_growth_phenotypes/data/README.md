# `binary_growth_phenotypes/data`

* `raw` holds data which was directly taken in the lab named by [date]\_[medium]\_[strain(s)].csv

The experiments were usually done with three biological replicates, if not it is indicated in the filename with 'NoRep'. 'Medium' refers to the base medium which was used for the experiment. The date refers to to the final time point measurement (meaning the log-phase transfer was done 24 hours before).

* `agg` holds tables which were created using the raw data files.
  * [medium]\_[OD].csv for the accumulated OD measurements per medium
  * [medium]\_[sig]\_[pairs].csv for the results of significance tests per medium

The column headers of [medium]\_[OD].csv: lab_mapping refers to the sample name used in the lab, short holds the medium composition, OD is the Optical Density at 600nm, strain is the strain, time is the time point of the measurement and sample refers to the three biological replicates. 

The column headers of [medium]\_[sig]\_[pairs].csv: strain is the strain, pval is the calculated p-value using `ttest_rel` for 0h and 24h pairs and `ttest_ind` for different medium composition pairs, significance refers to a common short form visualization where 'ns' means pval <= 1.00e+00, '\*': 1.00e-02 < p <= 5.00e-02 '\*\*': 1.00e-03 < p <= 1.00e-02 '\*\*\*': 1.00e-04 < p <= 1.00e-03 and '\*\*\*\*': p <= 1.00e-04 .

Strain mapping is as follows: '14':'TS', '15':'1197', '16':'1115' and '17':'1116'.