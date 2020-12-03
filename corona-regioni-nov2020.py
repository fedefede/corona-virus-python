# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 09:12:23 2020

@author: fede
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import folium

dataset_input = pd.read_csv('/home/fede/Desktop/corona-virus-python/COVID-19-master/dati-regioni/dpc-covid19-ita-regioni.csv')
dataset_popolazione = pd.read_csv('/home/fede/Dropbox/corona-virus/popolazione-regioni-2020.csv')
dataset_input['codice_regione'] = dataset_input['codice_regione'].replace([22],4)

dataset = pd.merge(dataset_input, dataset_popolazione, how = 'left', on = ["denominazione_regione" , "codice_regione"])
dataset['casi_per_100000_abitanti'] = dataset['totale_casi'] / dataset['abitanti']* 100000.
dataset['morti_per_100000_abitanti'] = dataset['deceduti'] / dataset['abitanti']* 100000.

X = dataset.iloc[:,:].values
X_last_update = dataset[-21:]

numero_regioni = (len(set(dataset['denominazione_regione'])))
print('numero delle regioni: ', numero_regioni)
dfs = {'df_regione_code_' + str(i):dataset[dataset['codice_regione']== i] for i in range(1, numero_regioni+1)}

date = pd.to_datetime(dfs['df_regione_code_1']['data'], format='%Y-%m-%d').dt.date

# region_list = []
# for i in range(numero_regioni):
#     name_region = 'df_regione_code_' + str(i+1)
#     region_list.append(name_region)
#     tamp_diff = np.diff(dfs[name_region]['tamponi'])
#     tamp_diff = np.insert(tamp_diff, 0, 0., axis=0)
#     deceduti_diff = np.diff(dfs[name_region]['deceduti'])
#     deceduti_diff = np.insert(deceduti_diff, 0, 0., axis=0)

#     fig = plt.figure(figsize=(25,10))
#     fig.suptitle('regione '+str(dfs[name_region].iloc[1,3]))
#     plt.subplot(331)
#     plt.plot(date,dfs[name_region].iloc[:,12])
#     plt.title(dfs[name_region].columns[12])
#     plt.subplot(332)
#     plt.plot(date,dfs[name_region].iloc[:,17])
#     plt.title(dfs[name_region].columns[17])
#     plt.subplot(336)
#     plt.plot(date,dfs[name_region].iloc[:,-1])
#     plt.title(dfs[name_region].columns[-1])    
#     plt.subplot(333)
#     plt.plot(date,dfs[name_region].iloc[:,-2])
#     plt.title(dfs[name_region].columns[-2])    
#     plt.subplot(334)
#     plt.plot(date,deceduti_diff)
#     plt.title('deceduti_giornalieri')
#     plt.subplot(335)
#     plt.plot(date,dfs[name_region].iloc[:,14])
#     plt.title(dfs[name_region].columns[14])
#     plt.subplot(337)
#     plt.plot(date,tamp_diff)
#     plt.title('tamponi_giornalieri')
#     plt.subplot(338)
#     plt.plot(date,dfs[name_region]['nuovi_positivi']/tamp_diff)
#     plt.ylim(0, 1)
#     plt.title('positive ratio')
#     plt.savefig("regione_{y}.png".format(y=str(dfs[name_region].iloc[1,3])))
#     plt.show()

region_geo = '/home/fede/Desktop/corona-virus-python/regioni.geojson'
    
my_map = folium.Map(location=[41.88, 12.48], zoom_start=5.5)
folium.Choropleth(geo_data = region_geo, data = X_last_update, columns=['denominazione_regione', 'totale_casi'], key_on='feature.properties.NOME_REG', nan_fill_color='white', fill_color='YlGnBu', fill_opacity=0.7, line_opacity=0.2, legend_name='totale casi').add_to(my_map)   
my_map.save('casi_totali.html')

my_map1 = folium.Map(location=[41.88, 12.48], zoom_start=5.5)
folium.Choropleth(geo_data = region_geo, data = X_last_update, columns=['denominazione_regione', 'morti_per_100000_abitanti'], key_on='feature.properties.NOME_REG', nan_fill_color='white', fill_color='YlGnBu', fill_opacity=0.7, line_opacity=0.2, legend_name='morti_per_100000_abitanti').add_to(my_map1)   
my_map1.save('morti_per_100000_abitanti.html')

my_map2 = folium.Map(location=[41.88, 12.48], zoom_start=5.5)
folium.Choropleth(geo_data = region_geo, data = X_last_update, columns=['denominazione_regione', 'casi_per_100000_abitanti'], key_on='feature.properties.NOME_REG', nan_fill_color='white', fill_color='YlGnBu', fill_opacity=0.7, line_opacity=0.2, legend_name='casi_per_100000_abitanti').add_to(my_map2)   
my_map2.save('casi_per_100000_abitanti.html')


# map = folium.Map(location=[41.88, 12.48], zoom_start=5.5)
# map.Choropleth(geo_data = region_geo, data = X_last_update, columns=['denominazione_regione', 'casi_per_100000_abitanti'], key_on='feature.properties.NOME_REG', nan_fill_color='white', fill_color='YlGnBu', fill_opacity=0.7, line_opacity=0.2, legend_name='casi_per_100000_abitanti')
# map.save('casi_per_100000_abitanti.html')