import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd
import h5py


BBHs = ['GW150914', 'GW151012', 'GW151226', 'GW170104', 'GW170608', 
        'GW170729', 'GW170809', 'GW170814', 'GW170818', 'GW170823']

a_BBH =  np.random.choice(BBHs)
print('We will use ', a_BBH, 'as an example of a BBH')
BBH_file = './GWTC1/'+a_BBH+'_GWTC-1.hdf5'
BBH = h5py.File(BBH_file, 'r')
print('This file contains four datasets: ', [i for i in BBH.keys()])


"""
# Parameter estimation sample release for GWTC-1

This page serves as a basic introduction to loading and viewing data released 
in associaton with the publication titled __Observations of Compact Binary Mergers 
by Advanced LIGO and Advanced Virgo during the First and Second Observing Runs__ avaliable 
through [DCC](https://dcc.ligo.org/LIGO-P1800307/public) and [arXiv](https://arxiv.org/).

>The data used in these tutorials can be downloaded from the public 
DCC page [LIGO-P1800370-v5](https://dcc.ligo.org/LIGO-P1800370/public).
"""



df = pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]
})


st.write(df)