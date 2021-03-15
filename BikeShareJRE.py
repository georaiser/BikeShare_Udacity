#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 00:21:55 2020

@author: hellraiser
"""
import time
import pandas as pd
import numpy as np
import difflib
import geopy.distance
#import networkx as nx
import osmnx as ox
ox.config(use_cache=True, log_console=False)
 
#%%
CITY_DATA = { 'chicago': 'data/Chicago_loc.csv',
              'new york': 'New York_loc.csv',
              'washington': 'Washington DC_loc.csv' }

monthsYear={'name': {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 
                     9: 'September', 10: 'October', 11: 'November', 12: 'December'}, 
                    'days': {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}}
#%%
def get_filters_console():
    """Asks user to specify a city, month, and day to analyze."""
    print('Hello! Let\'s explore some US bikeshare data!')
    print("\n Input City")
    print("\nYou must choose betwen: chicago - new york - washington")
    city = input("city:   ")
    city= city.lower()
    city1=''
    while city1 == '':        
        try:
            city1=difflib.get_close_matches(city, CITY_DATA)[0]
        except:
            print("\nYou must choose betwen: chicago - new york - washington")
            city = input("city:   ")
            city= city.lower()
    
    month1=''
    while month1=='':   
        print("\n Input Month Number (1 - 6). (leave blank for all months)")
        month= input("month:   ")  
        if month == '':
            if month == '':
                    month = 'all' 
                    month1=month
        try:            
            if 1<=int(month)<=6 :
                month1=month                    
        except:
            pass
        
    d=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    print("\n Input Day name. (leave blank for all Days)")
    print('\n', d)
    day= input("Day:   ")
    
    day1=''
    while day1=='':
        if day == '':
            day1 = 'all'
        else:
            day=day.lower()
            day=day.title()
            try:
                day1=difflib.get_close_matches(day, d )[0] 
            except:
                print("\n Input Day name. (leave blank for all Days)")
                print('\n', d)
                day= input("Day:   ")
           
    return city1, month, day1

#%%
def get_filters(city, month):
    city1=difflib.get_close_matches(city, CITY_DATA)[0]  
    if month != 'all':
        month1=list(monthsYear['name'].values()).index(month)+1
    else:
        month1='all'
    return city1, month1
#%%
def load_data(city1, month1, day):
    # load data file into a dataframe
    try:
        df = pd.read_csv(CITY_DATA[city1])
        # convert the Time column to datetime
        df['Start Time'] = pd.to_datetime(df['Start Time'])
        df['End Time'] = pd.to_datetime(df['End Time'])    
        # extract month and day of week from Start Time to create new columns
        df['month'] = df['Start Time'].dt.month
        df['day_of_week'] = df['Start Time'].dt.day_name()
    except:
        df=None        
    try:
        # filter 
        if month1 != 'all':    
            df = df[df['month'] == int(month1)]    
        if day != 'all':
            df = df[df['day_of_week'] == day.title()]
    except:
        pass 
    
    df2=df.copy()
    df3=df2[['Start Station','latitude_start', 'longitude_start']].copy()
    df3.rename(columns={'Start Station':'Station','latitude_start':'latitude','longitude_start':'longitude'}, inplace=True)
    df4=df2[['End Station','latitude_end', 'longitude_end']].copy()
    df4.rename(columns={'End Station':'Station','latitude_end':'latitude','longitude_end':'longitude'}, inplace=True)
    df5=df3.append(df4)

    df5.sort_values(by=['Station'], inplace=True)
    df5.drop_duplicates(subset ='Station', keep='first', inplace=True)
         
    print('-'*40)         
    return df,df5

#%%
def raw_data(df):
    count = 5
    while True:
        answer = input('Would you like to see 5 lines of raw data? Enter yes or no: ')
        # Check if response is yes, print the raw data and increment count by 5
        if answer == 'yes':
            print(df[0:count])
            count=count+5
        else:
            break
#%%
def getRoute(data): 
    
    distRec=np.zeros(len(data), order='C')
    for i in range (0, len(data.iloc[0:1])):
            try:   
                a=[data['latitude_start'].iloc[i],data['longitude_start'].iloc[i]]
                b=[data['latitude_end'].iloc[i],data['longitude_end'].iloc[i]]
                d=float(str(geopy.distance.great_circle(a,b)).split()[0])            
                '''bike,drive, mode'''
                # get a graph for some city
                if d != 0:
                    G = ox.graph_from_point([(a[0]+b[0])/2,(a[1]+b[1])/2],  dist= d*1200, network_type='bike')   
                else:
                    G = ox.graph_from_point([(a[0]+b[0])/2,(a[1]+b[1])/2],  dist= d+1200, network_type='bike')         
                # get the nearest network nodes to two lat/lng points
                orig = ox.get_nearest_node(G, (a))
                dest = ox.get_nearest_node(G, (b))            
                # find the shortest path between these nodes, minimizing travel time, then plot it
                route = ox.shortest_path(G, orig, dest, weight='length')
             
                #fig1, ax = ox.plot_graph_route(G, route, node_size=0, show=False, close=True, save=True, filepath='plot.png', bgcolor="#ffffff",edge_color="#85d3de")
                #ax.set_title(' Bike Route')
                
                # how long is our route in meters?
                edge_lengths = ox.utils_graph.get_route_edge_attributes(G, route, 'length')
                distRec[i]=sum(edge_lengths)/1000
            except:
                distRec[i]=np.nan                
        #print('distRec: =', distRec[i])
    return distRec, G, route

#%%
'''STATISTICS'''

def time_stats(df,city,month,day):
    # display the most common month
    commonMonth=monthsYear['name'][df.month.mode()[0]]
    print('\nThe Most Common Month : ', commonMonth)
    # display the most common day of week
    commonDay=df['day_of_week'].mode()[0]
    print('\nThe Most Common Day of Week : ', commonDay)
    # display the most common start hour
    commonHour=df['Start Time'].dt.hour.mode()[0]
    print('\nThe Most Common Hour : ', commonHour)
    #print('-'*40)
    return commonMonth, commonDay, commonHour

def station_stats(df):
    """Displays statistics on the most popular stations and trip.""" 
    # display most commonly used start station
    commonStartStation=df['Start Station'].mode()[0]
    print('\nThe Most Common Used Start Station : ', commonStartStation)
    # display most commonly used end station
    commonEndStation=df['End Station'].mode()[0]
    print('\nThe Most Common Used End Station : ', commonEndStation)
    # display most frequent combination of start station and end station trip
    #print('\n Please save or close the figure to continue ..') ## fig1, ax = ox.plot_graph_route
    df2=df.copy()
    df2['stations']=[df2['Start Station']+' / '+df2['End Station']][0]
    fr = df2['stations'].value_counts()
    dataFr=df2[df2['stations']==fr.index[0]]
    
    distRec, G, route = getRoute(dataFr)
    
    print('\nThe Most Common Combination of Start-End Station : \n', dataFr['Start Station'].iloc[0],' and ', dataFr['End Station'].iloc[0])
    print('\nThe Most Common Combination of Start-End Station Track (km): \n', distRec[0])
    print('\nThe Most Common Combination of Start-End Station Lineal Distance (km): \n', dataFr['Dist_lin_km'].iloc[0])
    print('-'*40)
    
    return commonStartStation, commonEndStation, G, route, dataFr, distRec

def trip_duration_stats(df):
    """Displays statistics on the total and average trip duration."""
    # display total travel time
    ttt=df['Trip Duration'].sum()
    print('\nThe total travel time : ', ttt)
    # display mean travel time
    ttm=df['Trip Duration'].mean()
    print('\nThe mean travel time : ', ttm)
    print('-'*40)
    
    return ttt, ttm

def user_stats(df):
    ut_subs, ut_cust, ut_subs_fem, ut_subs_male, ut_cust_fem, ut_cust_male=[],[],[],[],[],[]
    """Displays statistics on bikeshare users."""
    # Display counts of user types
    ut_subs=df[df['User Type']=='Subscriber']
    ut_cust=df[df['User Type']=='Customer']
    print('\nThe counts of user types "Subscriber" : ', len(ut_subs))
    print('\nThe counts of user types "Customer" : ', len(ut_cust))

    try:
        # Display counts of gender
        ut_subs_fem=ut_subs[ut_subs['Gender']=='Female']
        ut_subs_male=ut_subs[ut_subs['Gender']=='Male']
        
        ut_cust_fem=ut_cust[ut_cust['Gender']=='Female']
        ut_cust_male=ut_cust[ut_cust['Gender']=='Male']
        
        print('\nThe counts of user types "Subscriber" and Gender "Female": ', len(ut_subs_fem))
        print('\nThe counts of user types "Subscriber" and Gender "Male": ', len(ut_subs_male))
        print('\nThe counts of user types "Customer" and Gender "Female": ', len(ut_cust_fem))
        print('\nThe counts of user types "Customer" and Gender "Male": ', len(ut_cust_male))
    
        # Display earliest, most recent, and most common year of birth
        print('\nThe earliest year of birt: ', int(df['Birth Year'].min()))
        print('\nThe most recent year of birt: ', int(df['Birth Year'].max()))
        print('\nThe most common year of birt: ', int(df['Birth Year'].mode()))
    except:
        pass
    
    print('-'*40)
    return ut_subs, ut_cust, ut_subs_fem, ut_subs_male, ut_cust_fem, ut_cust_male
#%%    
def dfStats(df, df5, dataFr):
    df6=df5[df5['Station']==df['Start Station'].mode()[0]].iloc[0:1]
    df6=df6.append(df5[df5['Station']==df['End Station'].mode()[0]].iloc[0])
    df6=df6.append(df5[df5['Station']==dataFr['Start Station'].iloc[0]])
    df6=df6.append(df5[df5['Station']==dataFr['End Station'].iloc[0]])
    statName=['commonStart','commonEnd','commonStartCombination','commonEndCombination']
    df6['name']=statName
    return df6

#%%
def runAgain():
    while True:
        answer = input('Would you like to explore other US bikeshare data (yes or no): ')
        # Check if response is yes, print the raw data and increment count by 5
        if answer == 'yes':
            df,df5,df6=console()
        else:
            break
# get filter of data and show some statistics
def console():
    city1, month1, day = get_filters_console()
    df,df5 = load_data(city1, month1, day)
    raw_data(df)
    commonMonth, commonDay, commonHour=time_stats(df,city1,month1,day)
    commonStartStation, commonEndStation, G, route, dataFr, distRec=station_stats(df)
    ttt, ttm =trip_duration_stats(df)
    ut_subs, ut_cust, ut_subs_fem, ut_subs_male, ut_cust_fem, ut_cust_male =user_stats(df)
    df6=dfStats(df, df5, dataFr)
    fig1, ax = ox.plot_graph_route(G, route, node_size=0, show=True, close=True, save=True, filepath='plot.png', bgcolor="#ffffff",edge_color="#85d3de")
    ax.set_title(' Bike Route')
    return df,df5,df6

#df,df5,df6=console()
#runAgain()

#%%



















