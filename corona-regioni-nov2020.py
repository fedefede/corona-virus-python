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

date = list(pd.to_datetime(dfs['df_regione_code_1']['data'], format='%Y-%m-%d').dt.date)
last_day= date[-1]

X_italy_time_series = dataset.groupby(['data'], sort=False).agg({'terapia_intensiva':'sum',
                                                                            'totale_ospedalizzati':'sum',
                                                                            'totale_positivi':'sum',
                                                                            'nuovi_positivi':'sum',
                                                                            'dimessi_guariti':'sum',
                                                                            'deceduti':'sum',
                                                                            'totale_casi':'sum',
                                                                            'tamponi':'sum',
                                                                            'casi_testati':'sum',
                                                                            'abitanti':'sum'})

X_italy_time_series['deceduti_giornalieri'] = X_italy_time_series['deceduti'].diff(+1)
X_italy_time_series['tamponi_giornalieri'] = X_italy_time_series['tamponi'].diff(+1)

# Plots for national data
fig = plt.figure(figsize=(25,10))
fig.suptitle('valori nazionali')
plt.subplot(321)
plt.plot(date,X_italy_time_series.iloc[:,3])
plt.title(X_italy_time_series.columns[3])
plt.subplot(322)
plt.plot(date,X_italy_time_series.iloc[:,5])
plt.title(X_italy_time_series.columns[5])
plt.subplot(323)
plt.plot(date,X_italy_time_series.iloc[:,6])
plt.title(X_italy_time_series.columns[6])    
plt.subplot(324)
plt.plot(date,X_italy_time_series.iloc[:,7])
plt.title(X_italy_time_series.columns[7])    
plt.subplot(325)
plt.plot(date,X_italy_time_series['deceduti_giornalieri'])
plt.title('deceduti_giornalieri')
plt.subplot(326)
plt.plot(date,X_italy_time_series.iloc[:,3]/X_italy_time_series['tamponi_giornalieri'])
plt.title('positivity ratio')

plt.savefig("valori_nazionali.png")
plt.show()

region_list = []
last_daily_test = []

# Plots for regional data
for i in range(numero_regioni):
    name_region = 'df_regione_code_' + str(i+1)
    region_list.append(name_region)
    tamp_diff = np.diff(dfs[name_region]['tamponi'])
    tamp_diff = np.insert(tamp_diff, 0, 0., axis=0)
    # last_daily_test.append(tamp_diff[-1])
    deceduti_diff = np.diff(dfs[name_region]['deceduti'])
    deceduti_diff = np.insert(deceduti_diff, 0, 0., axis=0)
    last_daily_test.append([tamp_diff[-1], i+1])
    
    fig = plt.figure(figsize=(25,10))
    fig.suptitle('regione '+str(dfs[name_region].iloc[1,3]))
    plt.subplot(331)
    plt.plot(date,dfs[name_region].iloc[:,12])
    plt.title(dfs[name_region].columns[12])
    plt.subplot(332)
    plt.plot(date,dfs[name_region].iloc[:,17])
    plt.title(dfs[name_region].columns[17])
    plt.subplot(336)
    plt.plot(date,dfs[name_region].iloc[:,-1])
    plt.title(dfs[name_region].columns[-1])    
    plt.subplot(333)
    plt.plot(date,dfs[name_region].iloc[:,-2])
    plt.title(dfs[name_region].columns[-2])    
    plt.subplot(334)
    plt.plot(date,deceduti_diff)
    plt.title('deceduti_giornalieri')
    plt.subplot(335)
    plt.plot(date,dfs[name_region].iloc[:,14])
    plt.title(dfs[name_region].columns[14])
    plt.subplot(337)
    plt.plot(date,tamp_diff)
    plt.title('tamponi_giornalieri')
    plt.subplot(338)
    plt.plot(date,dfs[name_region]['nuovi_positivi']/tamp_diff)
    plt.ylim(0, 1)
    plt.title('positive ratio')
    plt.savefig("regione_{y}.png".format(y=str(dfs[name_region].iloc[1,3])))
    plt.show()
    
df_last_daily = pd.DataFrame(last_daily_test, columns=('daily_test', 'codice_regione'))
X_last_update_regions = dataset[-21:]

# Merge P.A. Bolzano and P.A. Trento, because the map has only the whole region
X_last_update_regions = pd.merge(X_last_update_regions, df_last_daily, how = 'inner', on = 'codice_regione')
X_last_update_regions['codice_regione'] = X_last_update_regions['codice_regione'].replace([21],4)
X_last_update_regions = X_last_update_regions.groupby(['codice_regione'], sort=False).agg({'terapia_intensiva':'sum',
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
                                                                            'lat regione':'sum',
                                                                            'long regione':'sum',
                                                                            'data':'first',
                                                                            'denominazione_regione': ' '.join})
X_last_update_regions['denominazione_regione'] = X_last_update_regions['denominazione_regione'].replace(['P.A. Bolzano P.A. Trento'],'Trentino-Alto Adige')

# Coloured maps with index per 100k population
X_last_update_regions['casi_per_100000_abitanti'] = X_last_update_regions['totale_casi'] / X_last_update_regions['abitanti']* 100000.
X_last_update_regions['morti_per_100000_abitanti'] = X_last_update_regions['deceduti'] / X_last_update_regions['abitanti']* 100000.
X_last_update_regions['positivity_rate'] = X_last_update_regions['nuovi_positivi'] / X_last_update_regions['daily_test']* 100

# url1 = 'https://gist.githubusercontent.com/datajournalism-it/48e29e7c87dca7eb1d29/raw/2636aeef92ba0770a073424853f37690064eb0ea/regioni.geojson'
region_geo = '/home/fede/Desktop/corona-virus-python/regioni.geojson'
lat_list = list(X_last_update_regions['lat regione'])
long_list = list(X_last_update_regions['long regione'])
region_name = list(X_last_update_regions['denominazione_regione'])

def make_map(df_to_map, column_to_map, legend_name):
    my_map = folium.Map(location=[41.88, 12.48], zoom_start=6)
    variable_list = list(df_to_map[column_to_map])
    legend_total = legend_name + ' al %s' % last_day
    folium.Choropleth(geo_data = region_geo, data = df_to_map, columns=['denominazione_regione', column_to_map], key_on='feature.properties.NOME_REG', nan_fill_color='white', fill_color='YlGnBu', fill_opacity=0.7, line_opacity=0.2, legend_name=legend_total).add_to(my_map)   
    for lat, long, region, variable_value in zip(lat_list, long_list, region_name, variable_list):
        folium.Marker(location = [lat, long], popup= ' %s in %s: %.2f' %(legend_name , region, variable_value), icon = folium.Icon()).add_to(my_map)
    my_map.save('%s.html' % column_to_map)
    
make_map(X_last_update_regions, 'totale_casi', 'numero totale di casi [da inizio pandemia]')    
make_map(X_last_update_regions, 'morti_per_100000_abitanti', 'morti per 100000 abitanti [da inizio pandemia]')    
make_map(X_last_update_regions, 'positivity_rate', 'positività [%%] (del giorno %s)' % last_day)   
print('fine') 


