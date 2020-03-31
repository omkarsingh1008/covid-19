from flask import Flask
from flask import Flask, render_template,request,session,redirect,url_for
import os,json
import pickle
import COVID19Py
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot  as plt
covid19 = COVID19Py.COVID19()
app=Flask(__name__)
@app.route('/')
def index():
	l = covid19.getLocations(rank_by='deaths')
	death=pd.DataFrame(columns=['country','deaths'])
	for i in range(5):
		death.loc[i,'country']=l[i]['country']
		death.loc[i,'deaths']=l[i]['latest']['deaths']#top five deaths cases in world
	l1 = covid19.getLocations(rank_by='confirmed')
	con=pd.DataFrame(columns=['country','confirmed'])
	for i in range(5):
		con.loc[i,'country']=l1[i]['country']
		con.loc[i,'confirmed']=l1[i]['latest']['confirmed']#top five confirmend cases in world


	return render_template('index.html',death=death.to_html(),con=con.to_html())
@app.route('/data/',methods=['POST'])
def data():

	num=request.form['fname'] # get city name

	fe=['name','rating','user_ratings_total','vicinity']
	city=num.replace(" ",'%20') #we are use google api to retrive data
	url="https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={}&inputtype=textquery&fields=photos,formatted_address,name,rating,opening_hours,geometry&key={}"
	url=url.format(city) # here we are format a city name in url
	page=requests.get(url)
	if page.status_code == 200 : #check data is get or not if code status is 200 means we get a data
		citys = page.json()
	else : 
		print("Check you internet connectivity or input")
	lat=citys['candidates'][0]['geometry']['location']['lat'] #here we get lat
	lng=citys['candidates'][0]['geometry']['location']['lng']
	fetures=['gas_station','grocery_or_supermarket','hospital','pharmacy','restaurant']
	data1=pd.DataFrame(columns=['category','name','rating','user_ratings_total','vicinity'])#creating a new dataframe
	index=0
	for fet in fetures:
		url="https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={},{}&rankby=distance&type={}&key={}"
		url=url.format(lat,lng,fet)
		page=requests.get(url)
		if page.status_code == 200 : 
			data = page.json()
		else : 
			print("Check you internet connectivity or input")
		for i in range(5):
			data1.loc[index,'category']=fet
			for j in fe:
				try:
					data1.loc[index,j]=data['results'][i][j]#insert a data into a Dataframe
				except:
					data1.loc[index,j]=0
			index=index+1
	covid_19=pd.read_csv('D:\\hackathon_Adhoc\\covid19-corona-virus-india-dataset\\complete.csv')
	covid_19=covid_19[covid_19['Name of State / UT']==citys['candidates'][0]['formatted_address'].split(',')[1][1:]] #get a confirmend  cases by state
	helps=pd.read_csv('D:\\hackathon_Adhoc\\coronvavirushelplinenumber (1).csv')
	try:
		number=helps[helps['Name of the State']==citys['candidates'][0]['formatted_address'].split(',')[1][1:]]['Helpline Nos.'].values[0]#get a help line number
	except:
		number="don't have "
	state=citys['candidates'][0]['formatted_address'].split(',')[1][1:]
	#print('stay home '*10)
	#print(data1)
	#print(type(num))
	return render_template('pridict.html',fname=num,covid_19=covid_19.to_html(),data_city=data1.to_html(),number=number,state=state)

if __name__ == '__main__':
	app.run()



	

