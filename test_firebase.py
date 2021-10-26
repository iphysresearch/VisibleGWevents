import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np

import firebase_admin
from firebase_admin import credentials, firestore, storage
import h5py
import io
import os
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt


st.set_page_config(
    page_title="Ex-stream-ly Cool App",
    page_icon=":shark:",
    layout="wide",#"centered",# "wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)
# components.html("""
# <script src='https://cdn.plot.ly/plotly-latest.min.js'/>
# <script async='async' id='MathJax-script' src='https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js' type='text/javascript'/>
# """)
# components.html('<script async src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-AMS-MML_CHTML"></script>')
# <script src="path-to-mathjax/MathJax.js?config=TeX-AMS_SVG"></script>
# <script async src="https://cdn.jsdelivr.net/npm/mathjax@2/MathJax.js?config=TeX-AMS-MML_CHTML"></script>
# os.environ['PLOTLY_MATHJAX_PATH'] = '~/Github/'
# import json
# key_dict = json.loads(st.secrets["textkey"])
# creds = service_account.Credentials.from_service_account_info(key_dict)

json = {
  "type": st.secrets["type"],
  "project_id": st.secrets["project_id"],
  "private_key_id": st.secrets["private_key_id"],
  "private_key": st.secrets["private_key"],
  "client_email": st.secrets["client_email"],
  "client_id": st.secrets["client_id"],
  "auth_uri": st.secrets["auth_uri"],
  "token_uri": st.secrets["token_uri"],
  "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
  "client_x509_cert_url": st.secrets["client_x509_cert_url"],
}


if not firebase_admin._apps:
    # https://stackoverflow.com/a/44501290/8656360
    # cred = credentials.Certificate("streamlit-visiblegwevents-firebase-adminsdk-p25un-af6ce7d332.json")
    cred = credentials.Certificate(json)
    # firebase_admin.initialize_app(cred)

    firebase_admin.initialize_app(cred, {
        'storageBucket': 'streamlit-visiblegwevents.appspot.com'
    })


@st.cache(allow_output_mutation=True, hash_funcs={"h5py._hl.files.File": hash})
def load_data(filename):
    bucket = storage.bucket()
    print(list(bucket.list_blobs()))
    # [<Blob: streamlit-visiblegwevents.appspot.com, 1-OGC.hdf, 1631809334625785>]
    print(bucket.get_blob(filename))
    # <Blob: streamlit-visiblegwevents.appspot.com, 1-OGC.hdf, 1631809334625785>
    b = bucket.get_blob(filename)
    return h5py.File(io.BytesIO(b.download_as_bytes()), 'r')


@st.cache(allow_output_mutation=True, hash_funcs={"h5py._hl.files.File": hash})
def load_posterior(addr):
    filename = f'2-ogc/posterior_samples/{addr}'
    bucket = storage.bucket()
    print(list(bucket.list_blobs()))
    print(bucket.get_blob(filename))
    b = bucket.get_blob(filename)
    return h5py.File(io.BytesIO(b.download_as_bytes()), 'r')


@st.cache
def add_name(addr, name):
    print(name)
    df = pd.DataFrame(dict(load_posterior(addr)['samples']))
    df['Candidate'] = f'GW{name}'
    df['total_mass'] = df.mass1 + df.mass2
    df['chirp_mass'] = (df.mass1 * df.mass2)**(3/5) / df['total_mass']**(1/5)
    return df


@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


OGC_selected = st.sidebar.selectbox(
    "How would you like to be contacted?",
    ("1-OGC", "2-OGC", "3-OGC")
)

filename = {
    "1-OGC": '1-ogc/1-OGC.hdf',
    "2-OGC": '2-ogc/2-OGC.hdf',
    "3-OGC": '3-ogc/3-OGC.hdf',
}
data_range = {
    "1-OGC": 'O1',
    "2-OGC": 'O1+O2',
    "3-OGC": 'O1+O2+O3',
}
st.title(OGC_selected)

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load data into the hdf5.
catalog = load_data(filename[OGC_selected])
print(filename[OGC_selected], 'is loaded!')
# Notify the reader that the data was successfully loaded.
data_load_state.text(f"Done! (using {filename[OGC_selected]})")



st.header('Introduction')
if OGC_selected=='1-OGC':
    st.write('https://github.com/gwastro/1-ogc')  # TODO
    st.write('https://arxiv.org/pdf/1811.01921.pdf')  # TODO
elif OGC_selected=='2-OGC':
    st.write('https://github.com/gwastro/2-ogc')  # TODO
    st.write('https://arxiv.org/pdf/1910.05331.pdf')  # TODO

# Get a numpy structured array of the candidate event properties.
catalog_radio = st.radio(
    'Get dataset based on the candidate event properties:',
    ('complete', 'bbh'))
catalog_desc = {
    'complete': 'compact binary mergers',
    'bbh': 'binary black holes',
}
candidates = catalog[catalog_radio]

with st.expander("See explanation"):
    st.write(f"The `complete` set is the full dataset from {OGC_selected}. The `bbh` set includes BBH candidates from a select portion of {OGC_selected}.",)
    if OGC_selected=='1-OGC':
        st.markdown('''
        Both datasets are structured arrays which have the following named columns. 
        Some of these columns give information specific to either the LIGO Hanford or Livingston detectors. Where this is the case, the name of the column is prefixed with either a `H1` or `L1`.

        | Key           | Description                                                                                                                         |
        |---------------|-------------------------------------------------------------------------------------------------------------------------------------|
        | name          | The designation of the candidate event. This is of the form 150812+12:23:04UTC.                                                     |
        | jd | Julian Date of the average between the Hanford and Livingston observed end times |
        | far           | The rate of false alarms with a ranking statistic as large or larger than this event. The unit is yr^-1.                                                                                                           |
        | stat          | The value of the ranking statistic for this candidate event.                                                                                       |
        | mass1         | The component mass of one compact object in the template waveform which found this candidate. Units in detector frame solar masses. |
        | mass2         | The component mass of the template waveform which found this candidate. Units in detector frame solar masses.                       |
        | spin1z        | The dimensionless spin of one of the compact objects for the template waveform which found this candidate.                                                                                                                                  |
        | spin2z        | The dimensionless spin of one of the compact objects for the template waveform which found this candidate.                                                                                                                                    |
        | {H1/L1}_end_time   | The time in GPS seconds when a fiducial point in the signal passes throught the detector. Typically this is near the time of merger.                                                                                                                              |                                                                                                                           |
        | {H1/L1}_snr        | The amplitude of the complex matched filter signal-to-noise observed.                                                                                                                                    |
        | {H1/L1}_coa_phase        | The phase (angle) of the complex matched filter signal-to-noise observed.                                                          |
        | {H1/L1}_reduced_chisq |  Value of the signal consistency test defined in this [paper](https://arxiv.org/abs/gr-qc/0405045). This is not calculated for all candidate events. In this case a value of 0 is substituted.                                                                                                                                  |
        | {H1/L1}_sg_chisq      |  Value of the signal consistency test defined in this [paper](https://arxiv.org/abs/1709.08974). This is not calculated for all candidate events. In this case a value of 1 is substituted.                                                                                                                     |
        | {H1/L1}_sigmasq       |   The integral of the template waveform divided by the power spectral density.

        The `/bbh` dataset also has the following additional columns.

        | Key           | Description                                                                                                                         |
        |---------------|-------------------------------------------------------------------------------------------------------------------------------------|
        | pastro |     The probability that this BBH candidate is of astrophysical origin.                                        |
        | tdr |        The fraction of signals with this ranking statistic and above which are astrophysical in origin.                                               |
        ''')
    elif OGC_selected=='2-OGC':
        st.markdown('''
        Both datasets are structured arrays which have the following named columns. Some of these columns give information specific to either the 
        LIGO Hanford, LIGO Livingston or Virgo detectors. Where this is the case, the name of the column is prefixed with either a `H1`, `L1`, or `V1`.

        | Key           | Description                                                                                                                         |
        |---------------|-------------------------------------------------------------------------------------------------------------------------------------|
        | name          | The designation of the candidate event. This is of the form 150812+12:23:04UTC.                                                     |
        | far           | The rate of false alarms with a ranking statistic as large or larger than this event. The unit is yr^-1.                                                                                                           |
        | stat          | The value of the ranking statistic for this candidate event.                                                                                       |
        | mass1         | The component mass of one compact object in the template waveform which found this candidate. Units in detector frame solar masses. |
        | mass2         | The component mass of the template waveform which found this candidate. Units in detector frame solar masses.                       |
        | spin1z        | The dimensionless spin of one of the compact objects for the template waveform which found this candidate.                                                                                                                                  |
        | spin2z        | The dimensionless spin of one of the compact objects for the template waveform which found this candidate.                                                                                                                                    |
        | {H1/L1/V1}_end_time   | The time in GPS seconds when a fiducial point in the signal passes throught the detector. Typically this is near the time of merger.                                                                                                                              |                                                                                                                           |
        | {H1/L1/V1}_snr        | The amplitude of the complex matched filter signal-to-noise observed.                                                                                                                                    |
        | {H1/L1/V1}_coa_phase        | The phase (angle) of the complex matched filter signal-to-noise observed.                                                          |
        | {H1/L1/V1}_reduced_chisq |  Value of the signal consistency test defined in this [paper](https://arxiv.org/abs/gr-qc/0405045). This is not calculated for all candidate events. In this case a value of 0 is substituted.                                                                                                                                  |
        | {H1/L1/V1}_sg_chisq      |  Value of the signal consistency test defined in this [paper](https://arxiv.org/abs/1709.08974). This is not calculated for all candidate events. In this case a value of 1 is substituted.                                                                                                                     |
        | {H1/L1/V1}_sigmasq       |   The integral of the template waveform divided by the power spectral density.

        The `/bbh` dataset also has the following additional column.

        | Key           | Description                                                                                                                         |
        |---------------|-------------------------------------------------------------------------------------------------------------------------------------|
        | pastro |     The probability that this BBH candidate is of astrophysical origin.                                        |
        ''')

if OGC_selected=='1-OGC':
    df = pd.DataFrame(np.asarray(candidates))
elif OGC_selected=='2-OGC':
    df = pd.DataFrame(dict(candidates))
    df['V1_GPS_time'] = df.V1_end_time.map(lambda x: str(x))

df["FAR^{-1}"] = df.far.map(lambda x: 1/x)
df["Designation"] = df.name.map(lambda x: x.decode())
df['snr_network'] = np.sqrt(df.H1_snr ** 2 + df.L1_snr ** 2 + (0 if OGC_selected=='1-OGC' else df.V1_snr))
df['chi_eff'] = (df.spin1z * df.mass1 + df.spin2z * df.mass2) / (df.mass1 + df.mass2)
df['H1_GPS_time'] = df.H1_end_time.map(lambda x: str(x))
df['L1_GPS_time'] = df.L1_end_time.map(lambda x: str(x))


with st.container():
    if st.checkbox('Show raw data'):
        st.subheader('Raw data')
        st.write(df)
    if st.checkbox('Show statistics for raw data'):
        st.subheader('Statistics')
        st.write(df.describe())


st.write('---')
st.header('Table')
st.write(f'Candidate events from the full search for {catalog_desc[catalog_radio]} in {data_range[OGC_selected]} data.')
num_head = st.select_slider(
    'Select the number of candidates sorted by FAR:',
    options=[10, 20, 50, 100, 500, 1000, None],
    value=20)
dddf = df.sort_values('far', ascending=True)[['Designation'] + (['jd'] if OGC_selected == '1-OGC' else [])
                                              +['far', "FAR^{-1}", 'stat', 
                                              'snr_network', 'H1_snr', 'L1_snr',] + ([] if OGC_selected == '1-OGC' else ['V1_snr'])
                                              + ['H1_GPS_time', 'L1_GPS_time'] + ([] if OGC_selected == '1-OGC' else ['V1_GPS_time'])
                                              + ['mass1', 'mass2', 'chi_eff']
                                              + (['pastro'] if catalog_radio == 'bbh' else [])
                                              + (['tdr'] if (OGC_selected == '1-OGC') and (catalog_radio=='bbh') else [])].set_index('Designation').head(num_head)
st.dataframe(dddf)
st.download_button(
    label="Download data as CSV",
    data=convert_df(dddf),
    file_name=f'{OGC_selected}_{catalog_radio}_head{num_head}.csv',
    mime='text/csv',
)


st.write('---')
st.header('Figure')
ddf = df[df.stat > 7.5].sort_values('stat')

# fig, ax = plt.subplots()
# cm = plt.cm.get_cmap('viridis_r')
# sc = plt.scatter(ddf.mass1, ddf.mass2,
#             s=ddf.stat*5,
#             c=ddf.stat,
#             vmin=7.5,
#             vmax=9,
#             cmap=cm)
# plt.colorbar(sc)
# plt.xscale('log')
# plt.yscale('log')
# plt.xlabel(r'$m_1$')
# plt.xlim(left=1)
# plt.ylim(bottom=1)
# st.pyplot(fig)


fig = go.Figure(data=[go.Scatter(
    x=ddf.mass1,
    y=ddf.mass2,
    mode='markers',
    marker=dict(
        color=ddf.stat,
        size=ddf.stat * (2 if OGC_selected == '1-OGC' else 1),
        showscale=True,
        colorbar=dict(
            title=r"Ranking Statistic",
        ),
        colorscale="Viridis_r",
        cmin=7.5,
        cmax=(9 if OGC_selected == '1-OGC' else 15)
    ),
    text=ddf.name.map(lambda x: f'Designation: {x.decode()}<br>') + ddf.stat.map(lambda x: f'Ranking Statistic: {x:.2f}'),
)]
)

fig.update_layout(
    title=f'Candidate events from the full search for {catalog_desc[catalog_radio]} in {data_range[OGC_selected]} data.',
    xaxis=dict(
        # title=r'$m_1$',  # TODO LaTeX is not working
        title='mass 1',
        gridcolor='white',
        type='log',
        gridwidth=2,
    ),
    yaxis=dict(
        title='mass 2',
        gridcolor='white',
        gridwidth=2,
        type='log',
    ),
    paper_bgcolor='rgb(243, 243, 243)',
    plot_bgcolor='rgb(243, 243, 243)',
    autosize=False,
    width=800,
    height=600,
    yaxis_range=[0, 1.8],
    xaxis_range=[0, 2.8],
)

st.plotly_chart(fig, use_container_width=True,
                include_plotlyjs='cdn', include_mathjax='cdn')  # TODO LaTeX is not working
# fig.show()

if OGC_selected=='2-OGC':
    with st.container():
        st.write(r'Marginalized `90%` credible region for all BBH candidates with $p_{\text {astro}} \ge 0.5$ (`stat`) '
                 'in source-frame componentmasses (left) along with source-frame total mass and effective spin (right).',)
        col1, col2 = st.columns(2)
        targets = [('H1L1V1-EXTRACT_POSTERIOR_150914_09H_50M_45UTC-0-1.hdf', '150914'), 
                   ('H1L1V1-EXTRACT_POSTERIOR_170814_10H_30M_43UTC-1-1.hdf', '170814'),
                   ('H1L1V1-EXTRACT_POSTERIOR_170823_13H_13M_58UTC-2-1.hdf', '170823'),
                   ('H1L1V1-EXTRACT_POSTERIOR_170104_21H_58M_40UTC-19-1.hdf', '170104'),
                   ('H1L1V1-EXTRACT_POSTERIOR_151226_03H_38M_53UTC-4-1.hdf', '151226'),
                   ('H1L1V1-EXTRACT_POSTERIOR_151012_09H_54M_43UTC-5-1.hdf', '151012'),
                   ('H1L1V1-EXTRACT_POSTERIOR_170809_08H_28M_21UTC-6-1.hdf', '170809'),
                   ('H1L1V1-EXTRACT_POSTERIOR_170729_18H_56M_29UTC-7-1.hdf', '170729'),
                   ('H1L1V1-EXTRACT_POSTERIOR_170608_02H_01M_16UTC-8-1.hdf', '170608'),
                   ('H1L1V1-EXTRACT_POSTERIOR_170121_21H_25M_36UTC-9-1.hdf', '170121'),
                   ('H1L1V1-EXTRACT_POSTERIOR_170818_02H_25M_09UTC-10-1.hdf', '170818'),
                   ('H1L1V1-EXTRACT_POSTERIOR_170727_01H_04M_30UTC-11-1.hdf', '170727'),
                   ('H1L1V1-EXTRACT_POSTERIOR_170304_16H_37M_53UTC-12-1.hdf', '170304'),
                   ('H1L1V1-EXTRACT_POSTERIOR_151205_19H_55M_25UTC-13-1.hdf', '151205'),
                   ]

        df = pd.concat([add_name(addr, name) for addr, name in targets])
        # https://plotly.com/python/2d-histogram-contour/#basic-2d-histogram-contour
        fig = px.density_contour(df, x="mass1", y="mass2", color='Candidate',
                                width=800, height=600, histnorm='percent',
                                range_x=[10, 80], range_y=[0, 60],
                                )
        # https://plotly.com/python/reference/contour/
        fig.update_traces(contours_showlabels=False,
                        contours_start=0.9,
                        contours_end=0.9,)
        fig.update_layout(
            xaxis=dict(
                # title=r'$m_1$',  # TODO LaTeX is not working
                title='mass 1 (source frame)',
                gridcolor='white',
                # type='log',
                gridwidth=2,
            ),
            yaxis=dict(
                title='mass 2 (sorce frame)',
                gridcolor='white',
                gridwidth=2,
                # type='log',
            ),
            paper_bgcolor='rgb(243, 243, 243)',
            plot_bgcolor='rgb(243, 243, 243)',
        )
        with col1:
            st.plotly_chart(fig, use_container_width=True,)

        fig = px.density_contour(df, x="total_mass", y="chi_eff", color='Candidate',
                                 width=800, height=600, histnorm='percent',
                                 range_x=[10, 130], range_y=[-0.6, 0.6],
                                 )
        # https://plotly.com/python/reference/contour/
        fig.update_traces(contours_showlabels=False,
                          contours_start=0.9,
                          contours_end=0.9,
                          )
        fig.update_layout(
            xaxis=dict(
                # title=r'$m_1$',  # TODO LaTeX is not working
                title='total mass (soruce frame)',
                gridcolor='white',
                # type='log',
                gridwidth=2,
            ),
            yaxis=dict(
                title='chi_eff',
                gridcolor='white',
                gridwidth=2,
                # type='log',
            ),
            paper_bgcolor='rgb(243, 243, 243)',
            plot_bgcolor='rgb(243, 243, 243)',
        )
        with col2:
            st.plotly_chart(fig, use_container_width=True,)

        targets = [
                ('H1L1V1-EXTRACT_POSTERIOR_151216_09H_24M_16UTC-17-1.hdf', '151216'),
                ('H1L1V1-EXTRACT_POSTERIOR_170201_11H_03M_12UTC-15-1.hdf', '170201'),
                ('H1L1V1-EXTRACT_POSTERIOR_151217_03H_47M_49UTC-14-1.hdf', '151217'),
                ('H1L1V1-EXTRACT_POSTERIOR_170629_04H_13M_55UTC-26-1.hdf', '170629'),
                ]

        df = pd.concat([add_name(addr, name) for addr, name in targets])

        fig = px.density_contour(df,
                                 x="chi_eff", y="chirp_mass", color='Candidate',
                                 labels=dict(
                                     GW151216='151216',
                                     GW170201='170201',
                                     GW151217='151217',
                                     GW170629='170629',
                                 ),
                                 width=800, height=500, histnorm='percent',
                                 range_x=[-0.3, 0.9], range_y=[5, 30], marginal_x='histogram', marginal_y='histogram',
                                 )
        st.plotly_chart(fig, use_container_width=False,)

st.header('License and Citation')
st.header('Acknowledgments')
st.balloons()