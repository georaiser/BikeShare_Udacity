#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 26 23:28:15 2020

@author: hellraiser
"""

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSlot
from BikeUI import Ui_MainWindow  # importing our generated file
import sys, os
from BikeShareJRE import get_filters, load_data, getRoute, time_stats, station_stats, trip_duration_stats, dfStats, user_stats
# Make sure that we are using QT5
import osmnx as ox
ox.config(use_cache=True, log_console=False)
from folium import FeatureGroup, LayerControl, Map, Marker, Circle
import io
import time
import datetime
import branca.colormap as cm
import matplotlib
import matplotlib.pyplot as plt 
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas 
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar 
from matplotlib.figure import Figure
import numpy as np
import pathlib
pathname = pathlib.Path(__file__).parent.absolute()
print(str(pathname))
#%%
class window(QtWidgets.QMainWindow):
    def __init__(self):    
        super(window, self).__init__()    
        self.ui = Ui_MainWindow()        
        self.ui.setupUi(self)
        self.figure = Figure(figsize=(10, 10), dpi=200)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)  
        self.ui.verticalLayout.addWidget(self.toolbar)
        self.ui.verticalLayout.addWidget(self.canvas)
        self.ui.pushButtonSubmit.clicked.connect(self.submit )
        self.ui.pushButtonCancel.clicked.connect(self.close)
        
        self.ui.radioButton_5.toggled.connect(self.Clicked_2)
        self.ui.radioButton_6.toggled.connect(self.Clicked_2)
        self.ui.radioButton_7.toggled.connect(self.Clicked_2)
        self.ui.radioButton_8.toggled.connect(self.Clicked_2)
        self.ui.radioButton_9.toggled.connect(self.Clicked_2)
        
        self.ui.radioButton_1.toggled.connect(self.Clicked_1)
        self.ui.radioButton_2.toggled.connect(self.Clicked_1)
        self.ui.radioButton_3.toggled.connect(self.Clicked_1)

    @pyqtSlot()
    def submit(self):
        
        city=str(self.ui.comboCity.currentText())
        month=str(self.ui.comboMonth.currentText())
        day=str(self.ui.comboDay.currentText())
        city1, month1=get_filters(city, month)   
        global df, df5, df6, gender_mean, female_mean, male_mean, user_subs, user_cust, user 
        global ut_subs, ut_cust, ut_subs_fem, ut_subs_male, ut_cust_fem, ut_cust_male               
        df,df5 = load_data(city1, month1, day)

        try:
            now = datetime.datetime.now()
            df['age']=now.year-df['Birth Year']
        except:
            df['age']=0
            pass
        try:
            female_mean=df[df['Gender']=='Female'].groupby('Start Station').mean()
            female_mean['count']=df[df['Gender']=='Female'].groupby('Start Station')['Id'].count()
            female_mean.drop(columns=['latitude_start','longitude_start','latitude_end','longitude_end'], inplace=True)
            male_mean=df[df['Gender']=='Male'].groupby('Start Station').mean()
            male_mean['count']=df[df['Gender']=='Male'].groupby('Start Station')['Id'].count()            
            gender_mean=male_mean.merge(female_mean, how='outer', left_index=True, right_index=True, suffixes=(' male', ' female'))
            gender_mean['count total']=gender_mean['count female']+gender_mean['count male']
            gender_mean['female percent']=(gender_mean['count female']/gender_mean['count total'])*100
        except:
            pass
        
        try:
            user_subs=df[df['User Type']=='Subscriber'].groupby('Start Station').mean()               
            user_subs['count']=df[df['User Type']=='Subscriber'].groupby('Start Station')['Id'].count()                          
            user_cust=df[df['User Type']=='Customer'].groupby('Start Station').mean()               
            user_cust['count']=df[df['User Type']=='Customer'].groupby('Start Station')['Id'].count()  
            
            user_cust.drop(columns=['latitude_start','longitude_start','latitude_end','longitude_end'], inplace=True)
            user=user_subs.merge(user_cust, how='outer', left_index=True, right_index=True, suffixes=(' subs', ' cust'))
            user.dropna(subset=['latitude_start'], inplace=True)
            user['count subs'] = user['count subs'].fillna(0)
            user['count cust'] = user['count cust'].fillna(0)              
            user['count total']=user['count subs']+user['count cust']
            user['subs percent']=(user['count subs']/user['count total'])*100
        except:
            pass
        
        # Statistics
        commonMonth, commonDay, commonHour = time_stats(df,city1,month1,day)
        commonStartStation, commonEndStation, G, route, dataFr, distRec =station_stats(df)
        ttt, ttm =trip_duration_stats(df)
        ut_subs, ut_cust, ut_subs_fem, ut_subs_male, ut_cust_fem, ut_cust_male = user_stats(df)
        df6=dfStats(df, df5, dataFr)
        
        tstat=[]
        tstat.append('Statistics on the most frequent times of travel')
        tstat.append('The Most Common Month : '+str(commonMonth))
        tstat.append('The Most Common Day : '+str(commonDay))
        tstat.append('The Most Common Hour : '+str(commonHour))
        
        tstat.append('\nStatistics on the most popular stations and trip')
        tstat.append('The Most Common Used Start Station : '+str(commonStartStation))
        tstat.append('The Most Common Used End Station : '+str(commonEndStation))
        
        tstat.append('\nStatistics on the most popular combination stations')
        tstat.append('The Most Common Combination of Start-End Station : '+str(dataFr['Start Station'].iloc[0])+' and '+str(dataFr['End Station'].iloc[0]))
        tstat.append('The Most Common Combination of Start-End Station Track (km): '+str(distRec[0]))
        tstat.append('The Most Common Combination of Start-End Station Lineal Distance (km): '+str(dataFr['Dist_lin_km'].iloc[0]))
        
        tstat.append('\nStatistics on the total and average trip duration')
        tstat.append('The total travel time : '+str(ttt))
        tstat.append('The mean travel time : '+str(ttm))
        
        tstat.append('\nDisplays statistics on bikeshare users and gender')
        tstat.append('The counts of user types "Subscriber" : '+str(len(ut_subs)))
        tstat.append('The counts of user types "Customer" : '+str(len(ut_cust)))
        try:            
            tstat.append('The counts of user types "Subscriber" and Gender "Female": '+str(len(ut_subs_fem)))
            tstat.append('The counts of user types "Subscriber" and Gender "Male": '+str(len(ut_subs_male)))
            tstat.append('The counts of user types "Customer" and Gender "Female": '+str(len(ut_cust_fem)))
            tstat.append('The counts of user types "Customer" and Gender "Male": '+str(len(ut_cust_male)))
        except:
            pass       
        try:
            tstat.append('\nDisplay earliest, most recent, and most common year of birth')
            tstat.append('The earliest year of birt: '+str(int(df['Birth Year'].min())))
            tstat.append('The most recent year of birt: '+str(int(df['Birth Year'].max())))
            tstat.append('The most common year of birt: '+str(int(df['Birth Year'].mode())))
        except:
            pass
     
        self.ui.textEdit.setText("\n".join(tstat))
        
        # Route Map
        graph_map = ox.plot_graph_folium(G, popup_attribute='name', edge_width=2, edge_color="#85d3de", zoom=8) 
        try:
            route_graph_map = ox.plot_route_folium(G, route, route_map=graph_map, popup_attribute='length', zoom=8)
        except:
            route_graph_map=graph_map

        locations = df6[['latitude', 'longitude']]
        locationlist = locations.values.tolist()
        for point in range(0, len(df6)):
            Marker(locationlist[point], popup=df6[['Station','name']].iloc[point].values).add_to(route_graph_map)  
        filepath = 'CommonStation_ShortestPath.html'
        route_graph_map.save(filepath)
        w = self.ui.webEngineView_1
        w.resize(740, 540) 
        self.url = QtCore.QUrl.fromLocalFile(str(pathname)+'/'+filepath)
        w.load(self.url)
        w.show()    

        ##Bike Stations
        maps = Map([df5['latitude'].mean(),df5['longitude'].mean()], zoom_start=10, control_scale=True, tiles="OpenStreetMap")     
        locations2 = df5[['latitude', 'longitude']]
        locationlist2 = locations2.values.tolist()
        group2 = FeatureGroup(name="Bike Stations")
        for point in range(0, len(locationlist2)):
            Marker(locationlist2[point], popup=df5[['Station','latitude', 'longitude']].iloc[point].values).add_to(group2)        
        group2.add_to(maps)        
        LayerControl().add_to(maps)     
        data = io.BytesIO()
        maps.save(data, close_file=False)
        m = self.ui.webEngineView_2
        m.setHtml(data.getvalue().decode())
        m.resize(740, 540)  
        maps.save("BikeStations.html")
        m.show()    
        maps.save(data, close_file=True)
        
        # initial map tab      
        maps = Map([df5['latitude'].mean(),df5['longitude'].mean()], zoom_start=10, control_scale=True, tiles="OpenStreetMap")     
        LayerControl().add_to(maps)    
        data = io.BytesIO()
        maps.save(data, close_file=False)
        m = self.ui.webEngineView_3
        m.setHtml(data.getvalue().decode())
        m.resize(740, 520)
        m.show()    
        maps.save(data, close_file=True)
        
        try:
            # initial Graphics        
            self.figure.clear()  
            labels = 'Male', 'Female'        
            sizes = [len(df[df['Gender']=='Male']), len(df[df['Gender']=='Female'])]       
            explode = (0, 0.1)               
            ax1 = self.figure.add_subplot(111) 
            ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')
            self.canvas.draw()
            self.show
        except:
            pass
                   
        # setting value to progress bar 
        for i in range(101):  
            time.sleep(0.04)               
            self.ui.progressBar.setValue(i)
    
    # Graphics tab
    @pyqtSlot()
    def Clicked_1(self):
        global df, df5, df6, gender_mean, female_mean, male_mean, user_subs, user_cust, user   
        global ut_subs, ut_cust, ut_subs_fem, ut_subs_male, ut_cust_fem, ut_cust_male               
        radioBtn = self.sender()
        if radioBtn.isChecked():
            if radioBtn.text()=='Gender':
                self.figure.clear() 
                try:
                    labels = 'Male', 'Female'        
                    sizes = [len(df[df['Gender']=='Male']), len(df[df['Gender']=='Female'])]       
                    explode = (0, 0.1)               
                    ax1 = self.figure.add_subplot(111) 
                    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', startangle=90)
                    ax1.axis('equal')
                    self.canvas.draw()
                    self.show
                except:
                    pass
                
            if radioBtn.text()=='User Type':
                self.figure.clear()
                labels_ut = 'Subscriber', 'Customer'
                sizes_ut = [len(ut_subs), len(ut_cust)]
                explode = (0, 0.1)                            
                ax1 = self.figure.add_subplot(111)
                ax1.pie(sizes_ut, explode=explode, labels=labels_ut, startangle=90, autopct='%1.1f%%')
                ax1.axis('equal')
                self.canvas.draw()
                self.show

            if radioBtn.text()=='User Type and Gender':
                self.figure.clear()
                labels_g = 'Male_Subs', 'Female_Subs'           
                sizes_g = [(len(ut_subs_male)*100)/len(ut_subs), (len(ut_subs_fem)*100)/len(ut_subs)] 
                explode = (0, 0.1)
                ax2 = self.figure.add_subplot(111)
                ax2.pie(sizes_g, explode=explode,labels=labels_g, startangle=90, autopct='%1.1f%%')
                ax2.axis('equal')               
                self.canvas.draw()
                self.show
                    
    # maps tab           
    @pyqtSlot()
    def Clicked_2(self):
        def percent(data,percent=None):
            index=[]
            for i in percent:
                index.append(data.quantile(i))
            return index
                      
        global df, df5, df6, gender_mean, female_mean, male_mean, user_subs, user_cust, user 
        global ut_subs, ut_cust, ut_subs_fem, ut_subs_male, ut_cust_fem, ut_cust_male               
        radioBtn = self.sender()
        if radioBtn.isChecked():
            if radioBtn.text()=='Trip Duration':
                ##Average Trip Duration map        
                maps = Map([df5['latitude'].mean(),df5['longitude'].mean()], zoom_start=10, control_scale=True, tiles="OpenStreetMap")     
                try:  
                    locations3a = df[['latitude_start', 'longitude_start','Trip Duration','Start Station','age']].copy() 
                    locations3=locations3a.groupby('Start Station').mean()
                    locations3.dropna(subset=['Trip Duration'], inplace=True)
                    index=percent(locations3['Trip Duration'],percent=[0.01,0.40,0.75,0.85,0.98])
                    colormap = cm.LinearColormap(colors=['blue', 'cyan', 'yellow','orange','red'],
                                                 vmin=locations3['Trip Duration'].quantile(0.01), vmax=locations3['Trip Duration'].quantile(0.98),
                                                 caption='Average Trip Duration (m.)', index=index)
                    locationlist3 = locations3.values.tolist()
                    group3 = FeatureGroup(name="Trip Duration")
                    for i in range (0, len(locationlist3)):
                        Circle(location=locationlist3[i][0:2], radius=150, fill=True, color=colormap(locationlist3[i][2]),
                               popup=locations3[['Trip Duration','age']].iloc[i]).add_to(group3)
                    group3.add_to(maps) 
                    colormap.add_to(maps)           
                except:
                    pass
                LayerControl().add_to(maps)            
                data = io.BytesIO()
                maps.save(data, close_file=False)
                m = self.ui.webEngineView_3
                m.setHtml(data.getvalue().decode())
                m.resize(740, 520)
                maps.save("TripDuration.html")
                m.show()    
                maps.save(data, close_file=True)
            
            # Gender map
            if radioBtn.text()=='Gender Map':
                ##female percent        
                maps = Map([df5['latitude'].mean(),df5['longitude'].mean()], zoom_start=10, control_scale=True, tiles="OpenStreetMap")
                try:
                    gm=gender_mean.dropna(subset=['count total'])
                    index=percent(gm['female percent'],percent=[0.01,0.25,0.60,0.85,0.99])
                    colormap = cm.LinearColormap(colors=['blue', 'cyan', 'yellow','orange','red'], 
                                                     vmin=gm['female percent'].quantile(0.01), vmax=gm['female percent'].quantile(0.99),
                                                     caption='Female Percent', index=index)
                    locationlist4 = gm[['latitude_start', 'longitude_start','female percent']].values.tolist()
                    group4 = FeatureGroup(name="Female Percent")
                    pop=gm[['Trip Duration female', 'age female', 'count female','female percent']]
                    for i in range (0, len(locationlist4)):
                        Circle(location=locationlist4[i][0:2], radius=150, fill=True, color=colormap(locationlist4[i][2]),
                               popup=pop.iloc[i]).add_to(group4)
                        
                    group4.add_to(maps) 
                    colormap.add_to(maps) 
                except:
                    pass
                LayerControl().add_to(maps)            
                data = io.BytesIO()
                maps.save(data, close_file=False)
                m = self.ui.webEngineView_3
                m.setHtml(data.getvalue().decode())
                m.resize(740, 520)
                maps.save("FemalePercent.html")
                m.show()    
                maps.save(data, close_file=True)
                
            ## age map 
            if radioBtn.text()=='Age Map':                     
                maps = Map([df5['latitude'].mean(),df5['longitude'].mean()], zoom_start=10, control_scale=True, tiles="OpenStreetMap")
                try:
                    age=df.groupby('Start Station').mean()
                    age.dropna(subset=['age'], inplace=True)
                    index=percent(age['age'],percent=[0.01,0.25,0.50,0.75,0.99])
                    colormap = cm.LinearColormap(colors=['blue', 'cyan', 'yellow','orange','red'], 
                                                     vmin=age['age'].quantile(0.01), vmax=age['age'].quantile(0.99),
                                                     caption='Age Average', index=index)
                    locationlist5 = age[['latitude_start', 'longitude_start','age']].values.tolist()
                    group5 = FeatureGroup(name="Age Average")
                    pop=gender_mean[['age male', 'count male','age female', 'count female']]
                    for i in range (0, len(locationlist5)):
                        Circle(location=locationlist5[i][0:2], radius=150, fill=True, color=colormap(locationlist5[i][2]),
                               popup=pop.iloc[i]).add_to(group5)
                        
                    group5.add_to(maps) 
                    colormap.add_to(maps) 
                except:
                    pass
                LayerControl().add_to(maps)            
                data = io.BytesIO()
                maps.save(data, close_file=False)
                m = self.ui.webEngineView_3
                m.setHtml(data.getvalue().decode())
                m.resize(740, 520)
                maps.save("AgeAverage.html")
                m.show()    
                maps.save(data, close_file=True)
                
            ## Trip Count
            if radioBtn.text()=='Trip Count':               
                maps = Map([df5['latitude'].mean(),df5['longitude'].mean()], zoom_start=10, control_scale=True, tiles="OpenStreetMap")
                
                count=df.groupby('Start Station').mean()
                count['count']=df.groupby('Start Station')['Trip Duration'].count() 
                count.dropna(subset=['count'], inplace=True)
                index=percent(count['count'],percent=[0.05,0.40,0.75,0.95])
                colormap = cm.LinearColormap(colors=['blue', 'cyan', 'yellow','orange','red'], 
                                                 vmin=count['count'].quantile(0.05), vmax=count['count'].quantile(0.95),
                                                 caption='Trip Count Start Station',index=index)
                locationlist6 = count[['latitude_start', 'longitude_start','count']].values.tolist()
                group6 = FeatureGroup(name="Trip Count")
                pop=count[['Trip Duration', 'count', 'age']]
                for i in range (0, len(locationlist6)):
                    Circle(location=locationlist6[i][0:2], radius=150, fill=True, color=colormap(locationlist6[i][2]),
                           popup=pop.iloc[i]).add_to(group6)                    
                group6.add_to(maps) 
                colormap.add_to(maps)                
                LayerControl().add_to(maps)            
                data = io.BytesIO()
                maps.save(data, close_file=False)
                m = self.ui.webEngineView_3
                m.setHtml(data.getvalue().decode())
                m.resize(740, 520)
                maps.save("TripCount.html")
                m.show()    
                maps.save(data, close_file=True)
                
            ## User Type
            if radioBtn.text()=='User Type':               
                maps = Map([df5['latitude'].mean(),df5['longitude'].mean()], zoom_start=10, control_scale=True, tiles="OpenStreetMap")
                index=percent(user['subs percent'],percent=[0.01,0.10,0.40,0.70,0.95])
                colormap = cm.LinearColormap(colors=['blue', 'cyan', 'yellow','orange','red'], 
                                                 vmin=user['subs percent'].quantile(0.01), vmax=user['subs percent'].quantile(0.95),
                                                 caption='User Type: Subscriber (Percent)', index=index)
                
                locationlist7 = user[['latitude_start', 'longitude_start','subs percent']].values.tolist()
                group7 = FeatureGroup(name="User Type")
                pop=user[['count subs', 'count cust', 'subs percent']]
                for i in range (0, len(locationlist7)):
                    Circle(location=locationlist7[i][0:2], radius=150, fill=True, color=colormap(locationlist7[i][2]),
                           popup=pop.iloc[i]).add_to(group7)                    
                group7.add_to(maps) 
                colormap.add_to(maps)                
                LayerControl().add_to(maps)            
                data = io.BytesIO()
                maps.save(data, close_file=False)
                m = self.ui.webEngineView_3
                m.setHtml(data.getvalue().decode())
                m.resize(740, 520)
                maps.save("UserType.html")
                m.show()    
                maps.save(data, close_file=True)   
                
                
                
app = QtWidgets.QApplication([])
application = window()
application.show()
sys.exit(app.exec())
