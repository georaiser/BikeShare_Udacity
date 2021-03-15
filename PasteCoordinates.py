#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 02:18:48 2020

@author: hellraiser
"""

import numpy as np
import pandas as pd
import os
import geopy.distance

CITY_DATA = { 'Chicago': ['chicago.csv','Divvy_Stations_2017_Q3Q4.csv'],
              'New York': ['new_york_city.csv','201709-citibike-tripdata.csv','201710-citibike-tripdata.csv'],
              'Washington DC': ['washington.csv', '202008-capitalbikeshare-tripdata.csv'] }

path=r'/mnt/DiscoD/Udacity/DataAnalyticsFundamentals_NanoDegree/Project_2'
os.chdir(path)
#%%
def distLin(data):
# lineal distance between stations
    dist_lin=np.zeros(len(data), order='C')
    start=data[['latitude_start','longitude_start']].values
    end=data[['latitude_end','longitude_end']].values  
    
    for i in range (0, len(data)):
        try:       
            d=geopy.distance.great_circle(start[i],end[i])
            dist_lin[i]=float(str(d).split()[0])           
        except:
            dist_lin[i]=np.nan
    return dist_lin
        
#%%
city = 'Chicago' 
df = pd.read_csv(CITY_DATA[city][0])
print(df.head())
df['Id']=df['Unnamed: 0']
df.drop(["Unnamed: 0"], axis=1, inplace = True) 

cd=pd.read_csv('auxCoord/'+CITY_DATA[city][1])
print(cd.head())

st1=cd[['name', 'latitude', 'longitude']].copy()
#st1.sort_values(by=['start_station_name'], inplace=True)
#st1=cd.drop_duplicates(subset ='start_station_name', keep='first')[['start_station_name','start_station_id', 'start_lat', 'start_lng']].copy()
st1.rename(columns={'name':'Start Station','latitude':'latitude_start','longitude':'longitude_start'}, inplace=True)
merged1 = pd.merge(df, st1, on=["Start Station"], how='outer')

st2=cd[['name', 'city', 'latitude', 'longitude']].copy()
#st1.sort_values(by=['end_station_name'], inplace=True)
#st2=cd.drop_duplicates(subset ='end_station_name', keep='first')[['end_station_name','end_station_id', 'end_lat', 'end_lng']].copy()
st2.rename(columns={'name':'End Station','latitude':'latitude_end','longitude':'longitude_end'}, inplace=True)
merged2 = pd.merge(merged1, st2, on=["End Station"], how='outer')

merged2.dropna(subset = ['latitude_start'], inplace=True)
merged2.dropna(subset = ['latitude_end'], inplace=True)

dist_lin=distLin(merged2)
merged2['Dist_lin_km']=dist_lin

merged2.to_csv(city+'_loc.csv', sep=",", index=False)    
#%%   
city = 'New York' 
df = pd.read_csv(CITY_DATA[city][0])
print(df.head())
df['Id']=df['Unnamed: 0']
df.drop(["Unnamed: 0"], axis=1, inplace = True) 

cd=pd.read_csv('auxCoord/'+CITY_DATA[city][1])
print(cd.head())
cd1=pd.read_csv('auxCoord/'+CITY_DATA[city][2])
print(cd.head())

# get coordinates, rename columns, join dataFrame and drop duplicates
st1=cd[['start station name', 'start station latitude', 'start station longitude']].copy()
st1.rename(columns={'start station name':'Station','start station latitude':'latitude','start station longitude':'longitude'}, inplace=True)
st2=cd[['end station name', 'end station latitude', 'end station longitude']].copy()
st2.rename(columns={'end station name':'Station','end station latitude':'latitude','end station longitude':'longitude'}, inplace=True)

st3=cd1[['start station name', 'start station latitude', 'start station longitude']].copy()
st3.rename(columns={'start station name':'Station','start station latitude':'latitude','start station longitude':'longitude'}, inplace=True)
st4=cd1[['end station name', 'end station latitude', 'end station longitude']].copy()
st4.rename(columns={'end station name':'Station','end station latitude':'latitude','end station longitude':'longitude'}, inplace=True)

st5= st1.append([st2,st3,st4])

st5.sort_values(by=['Station'], inplace=True)
st5.drop_duplicates(subset ='Station', keep='first', inplace=True)

merged1 = pd.merge(df, st5, left_on='Start Station', right_on='Station', how='outer')
merged2 = pd.merge(merged1, st5, left_on='End Station', right_on='Station', how='outer')

# rename and drop
merged2.rename(columns={'latitude_x':'latitude_start','longitude_x':'longitude_start', }, inplace=True)
merged2.rename(columns={'latitude_y':'latitude_end','longitude_y':'longitude_end'}, inplace=True)
merged2.drop(['Station_x','Station_y'], axis=1, inplace = True)

merged2.dropna(subset = ['latitude_start'], inplace=True)
merged2.dropna(subset = ['latitude_end'], inplace=True)

dist_lin=distLin(merged2)
merged2['Dist_lin_km']=dist_lin

merged2.to_csv(city+'_loc.csv', sep=",", index=False)    
#%%
city = 'Washington DC' 
df = pd.read_csv(CITY_DATA[city][0])
print(df.head())
df['Id']=df['Unnamed: 0']
df.drop(["Unnamed: 0"], axis=1, inplace = True) 

cd=pd.read_csv('auxCoord/'+CITY_DATA[city][1])
print(cd.head())

# get coordinates, rename columns, join dataFrame and drop duplicates
st1=cd[['start_station_name', 'start_lat', 'start_lng']].copy()
st1.rename(columns={'start_station_name':'Station','start_lat':'latitude','start_lng':'longitude'}, inplace=True)
st2=cd[['end_station_name', 'end_lat', 'end_lng']].copy()
st2.rename(columns={'end_station_name':'Station','end_lat':'latitude','end_lng':'longitude'}, inplace=True)

st3= st1.append([st2])
st3.dropna(subset = ['Station'], inplace=True)
st3.sort_values(by=['Station'], inplace=True)
st3.drop_duplicates(subset ='Station', keep='first', inplace=True)

merged1 = pd.merge(df, st3, left_on='Start Station', right_on='Station', how='outer')
merged2 = pd.merge(merged1, st3, left_on='End Station', right_on='Station', how='outer')

merged2.rename(columns={'latitude_x':'latitude_start','longitude_x':'longitude_start', }, inplace=True)
merged2.rename(columns={'latitude_y':'latitude_end','longitude_y':'longitude_end'}, inplace=True)
merged2.drop(['Station_x','Station_y'], axis=1, inplace = True)

merged2.dropna(subset = ['latitude_start'], inplace=True)
merged2.dropna(subset = ['latitude_end'], inplace=True)

dist_lin=distLin(merged2)
merged2['Dist_lin_km']=dist_lin

merged2.to_csv(city+'_loc.csv', sep=",", index=False)    


    