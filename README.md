Huginn - an Active Learning system for Metabolic Network Models development

0. Copyright info:
I, Robert Rozanski, the copyright holder of this work (software, figures and data files), release this work into the public domain. This applies worldwide. In some countries this may not be legally possible; if so: I grant anyone the right to use this work for any purpose, without any conditions, unless such conditions are required by law.

1. Dependencies:
  1. Python 3.4.0 with following modules (most of them should be installed by default):
    * re
    * sys
    * time
    * copy
    * random
    * pickle
    * traceback
    * subprocess
    * multiprocessing
  2. gringo 3.0.5: http://sourceforge.net/projects/potassco/
  3. clasp version 3.0.3: http://sourceforge.net/projects/potassco/
  4. XHAIL (System for eXtended Hybrid Abductive Inductive Learning) https://github.com/stefano-bragaglia/XHAIL
Note that ```./temp/xhail.sh``` must be edited to point to gringo and clasp
		

2. Usage:
To run existing test cases use command ```./evaluator.py > log```. The process will print many warnings that can be safely ignored. Important information will be saved in the log file as well as in the ```./pickled_archives``` folder. The latter can be read and analysed using functions from the ```./development_analysis.py``` file.


3. Additional files:
```./analysis_files.zip``` and ```./figures.zip``` contain files used in preparation of a manuscript about Huginn for the 13th conference on Computational Methods for Systems Biology.
