
import argopy
import bgcArgoDMQC as bgc

index = argopy.ArgoIndex(index_file='bgc-b').load().to_dataframe()
index = index.loc[index.dac == 'meds']

for wmo in index.wmo.unique():
    bgc.io.get_argo(wmo, local_path=bgc.io.Path.ARGO_PATH, ftype='summary')