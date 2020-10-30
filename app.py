import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd
import h5py
# import os
import time

BBHs = ['GW150914', 'GW151012', 'GW151226', 'GW170104', 'GW170608', 
        'GW170729', 'GW170809', 'GW170814', 'GW170818', 'GW170823']

# a_BBH =  np.random.choice(BBHs)
# a_BBH = 'GW150914'

############## For a target GW event ###########

a_BBH = st.sidebar.selectbox(      # Use a selectbox for options (on the sidebar)
    'Which GW event do you like best?', BBHs)

# option = st.selectbox(              # Use a selectbox for options (on the content)
#     'Which number do you like best?',
#      [i for i in BBH.keys()])


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

chart_data = pd.DataFrame(
     np.random.randn(20, 3),
     columns=['a', 'b', 'c'])

st.line_chart(chart_data)


if st.checkbox('Show dataframe'):   # Use checkboxes to show/hide data
    chart_data = pd.DataFrame(
       np.random.randn(20, 3),
       columns=['a', 'b', 'c'])

    st.line_chart(chart_data)


# 'Starting a long computation...'
# # Add a placeholder
# latest_iteration = st.empty()
# bar = st.progress(0)
# for i in range(100):
#   # Update the progress bar with each iteration.
#   latest_iteration.text(f'Iteration {i+1}')
#   bar.progress(i + 1)
#   time.sleep(0.1)
# '...and now we\'re done!'

'For', a_BBH

df_func = lambda name: pd.DataFrame(data = BBH[(name)].value)
df = pd.DataFrame( [df_func(name).median(axis=0) for name in BBH.keys()], index=[name for name in BBH.keys()])
st.write(df)
