WORKFLOW

* loadAnonymiseAll.Rmd is run first, which calls readInAllFiles.R, anonymises data to generate dataAnonymized/PSYC1anonymizes.rda and .csv

Then looks like demographicsAndExclusions.Rmd is run, which loads above data and strips out those who don't consent and reports some demographics, and creates file PSYC1_dfAfterConsentPracticeTrialsExclusions.rda

TO-DO
* recover right correct
* Analyse mixed-effects with lmer (good tutorial: https://www.sciencedirect.com/science/article/pii/S0749596X07001398) or brms for Bayesian.
TO-DO
* recover right correct
* Analyse mixed-effects with lmer (good tutorial: https://www.sciencedirect.com/science/article/pii/S0749596X07001398) or brms for Bayesian.
