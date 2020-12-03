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

url = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv'
dataset_input = pd.read_csv(url)

# dataset_input = pd.read_csv('/home/fede/Desktop/corona-virus-python/COVID-19-master/dati-regioni/dpc-covid19-ita-regioni.csv')
# df2 = pd.DataFrame(np.array([[3,'Lombardia',10103969],[12,'Lazio',5865544],[15,'Campania',5785861],[19,'Sicilia',4968410],[5,'Veneto',4907704],
#                              [8,'Emilia-Romagna',4467118],[1,'Piemonte',4341375],[16,'Puglia',4008296],[9,'Toscana',3722729],[18,'Calabria',1924701],
#                              [20,'Sardegna',1630474],[7,'Liguria',1543127],[11,'Marche',1518400],[13,'Abruzzo',1305770],[6,'Friuli Venezia Giulia',1211357],
#                              [4,'P.A. Trento',538223],[10,'Umbria',880285],[17,'Basilicata',556934],[14,'Molise',302265],[2,'Valle d\'Aosta',125501],
#                              [21,'P.A. Bolzano',520891]]), columns=['codice_regione', 'denominazione_regione', 'abitanti'])
dataset_popolazione = pd.read_csv('/home/fede/Dropbox/corona-virus/popolazione-regioni-2020.csv')

dataset_input['codice_regione'] = dataset_input['codice_regione'].replace([22],4)
dataset = pd.merge(dataset_input, dataset_popolazione, how = 'left', on = ["denominazione_regione" , "codice_regione"])
dataset['casi_per_100000_abitanti'] = dataset['totale_casi'] / dataset['abitanti']* 100000.
dataset['morti_per_100000_abitanti'] = dataset['deceduti'] / dataset['abitanti']* 100000.

numero_regioni = (len(set(dataset['denominazione_regione'])))
print('numero delle regioni: ', numero_regioni)
dfs = {'df_regione_code_' + str(i):dataset[dataset['codice_regione']== i] for i in range(1, numero_regioni+1)}

date = pd.to_datetime(dfs['df_regione_code_1']['data'], format='%Y-%m-%d').dt.date

region_list = []
last_daily_test = []

for i in range(numero_regioni):
    name_region = 'df_regione_code_' + str(i+1)
    region_list.append(name_region)
    tamp_diff = np.diff(dfs[name_region]['tamponi'])
    tamp_diff = np.insert(tamp_diff, 0, 0., axis=0)
    # last_daily_test.append(tamp_diff[-1])
    deceduti_diff = np.diff(dfs[name_region]['deceduti'])
    deceduti_diff = np.insert(deceduti_diff, 0, 0., axis=0)
    last_daily_test.append([tamp_diff[-1], i+1])

    # fig = plt.figure(figsize=(25,10))
    # fig.suptitle('regione '+str(dfs[name_region].iloc[1,3]))
    # plt.subplot(331)
    # plt.plot(date,dfs[name_region].iloc[:,12])
    # plt.title(dfs[name_region].columns[12])
    # plt.subplot(332)
    # plt.plot(date,dfs[name_region].iloc[:,17])
    # plt.title(dfs[name_region].columns[17])
    # plt.subplot(336)
    # plt.plot(date,dfs[name_region].iloc[:,-1])
    # plt.title(dfs[name_region].columns[-1])    
    # plt.subplot(333)
    # plt.plot(date,dfs[name_region].iloc[:,-2])
    # plt.title(dfs[name_region].columns[-2])    
    # plt.subplot(334)
    # plt.plot(date,deceduti_diff)
    # plt.title('deceduti_giornalieri')
    # plt.subplot(335)
    # plt.plot(date,dfs[name_region].iloc[:,14])
    # plt.title(dfs[name_region].columns[14])
    # plt.subplot(337)
    # plt.plot(date,tamp_diff)
    # plt.title('tamponi_giornalieri')
    # plt.subplot(338)
    # plt.plot(date,dfs[name_region]['nuovi_positivi']/tamp_diff)
    # plt.ylim(0, 1)
    # plt.title('positive ratio')
    # plt.savefig("regione_{y}.png".format(y=str(dfs[name_region].iloc[1,3])))
    # plt.show()
    
df_last_daily = pd.DataFrame(last_daily_test, columns=('daily_test', 'codice_regione'))
X_last_update3 = dataset[-21:]
X_last_update3 = pd.merge(X_last_update3, df_last_daily, how = 'inner', on = 'codice_regione')

X_last_update3['codice_regione'] = X_last_update3['codice_regione'].replace([21],4)
X_last_update3 = X_last_update3.groupby(['codice_regione'], sort=False).agg({'terapia_intensiva':'sum',
                                                                            'totale_ospedalizzati':'sum',
                                                                            'totale_positivi':'sum',
                                                                            'nuovi_positivi':'sum',
                                                                            'dimessi_guariti':'sum',
                                                                            'deceduti':'sum',
                                                                            'totale_casi':'sum',
                                                                            'tamponi':'sum',
                                                                            'casi_testati':'sum',
                                                                            'abitanti':'sum',
                                                                            'daily_test':'sum',
                                                                            'denominazione_regione': ' '.join})

X_last_update3['denominazione_regione'] = X_last_update3['denominazione_regione'].replace(['P.A. Bolzano P.A. Trento'],'Trentino-Alto Adige')
X_last_update3['casi_per_100000_abitanti'] = X_last_update3['totale_casi'] / X_last_update3['abitanti']* 100000.
X_last_update3['morti_per_100000_abitanti'] = X_last_update3['deceduti'] / X_last_update3['abitanti']* 100000.
# print('fino a qui fungeeeee!!!')
X_last_update3['positivity_rate'] = X_last_update3['nuovi_positivi'] / X_last_update3['daily_test']

# url1 = 'https://gist.githubusercontent.com/datajournalism-it/48e29e7c87dca7eb1d29/raw/2636aeef92ba0770a073424853f37690064eb0ea/regioni.geojson'
region_geo = '/home/fede/Desktop/corona-virus-python/regioni.geojson'
my_map = folium.Map(location=[41.88, 12.48], zoom_start=5.5)
folium.Choropleth(geo_data = region_geo, data = X_last_update3, columns=['denominazione_regione', 'totale_casi'], key_on='feature.properties.NOME_REG', nan_fill_color='white', fill_color='YlGnBu', fill_opacity=0.7, line_opacity=0.2, legend_name='totale casi').add_to(my_map)   
my_map.save('casi_totali.html')

my_map1 = folium.Map(location=[41.88, 12.48], zoom_start=5.5)
folium.Choropleth(geo_data = region_geo, data = X_last_update3, columns=['denominazione_regione', 'morti_per_100000_abitanti'], key_on='feature.properties.NOME_REG', nan_fill_color='white', fill_color='YlGnBu', fill_opacity=0.7, line_opacity=0.2, legend_name='morti_per_100000_abitanti').add_to(my_map1)   
my_map1.save('morti_per_100000_abitanti.html')

my_map2 = folium.Map(location=[41.88, 12.48], zoom_start=5.5)
folium.Choropleth(geo_data = region_geo, data = X_last_update3, columns=['denominazione_regione', 'casi_per_100000_abitanti'], key_on='feature.properties.NOME_REG', nan_fill_color='white', fill_color='YlGnBu', fill_opacity=0.7, line_opacity=0.2, legend_name='casi_per_100000_abitanti').add_to(my_map2)   
my_map2.save('casi_per_100000_abitanti.html')

my_map3 = folium.Map(location=[41.88, 12.48], zoom_start=5.5)
folium.Choropleth(geo_data = region_geo, data = X_last_update3, columns=['denominazione_regione', 'positivity_rate'], key_on='feature.properties.NOME_REG', nan_fill_color='white', fill_color='YlGnBu', fill_opacity=0.7, line_opacity=0.2, legend_name='positivity rate for the last update').add_to(my_map3)   
my_map3.save('positivity_rate.html')
