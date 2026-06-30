
import argopy
import bgcArgoDMQC as bgc

idx = argopy.ArgoIndex(index_file='bgc-b').query.compose({'dac':'meds', 'params':'CHLA'})
for wmo in idx.read_wmo():
    bgc.io.get_argo(wmo, mission='B', local_path='../data/chla_reprocess/')