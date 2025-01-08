#ARN beta Version with bigboy and interface
import pandas as pd
import pydeck as pdk
from pydeck.types import String
import numpy as np
import streamlit as st
import string
from geopy import distance
import csv
import time as Time
import datetime as dt
import cutout as cutout
from AddInBigBoy import update_location_data as BigBoyLayer

week = ["Mo","Tu","Wd","Th","Fr","Sa","Su"]
weekfull = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
slot = ["T1","T2","T3","T4","T5","T6","T7","T8","T9","T10","T11","T12"]
nowtime= str(dt.datetime.now().time())
bettertime = nowtime[:5].replace(':','')

st.set_page_config(layout="wide")
st.image('https://github.com/FoxGodTodd/ARNie/raw/main/ARNbanner.png',use_column_width=True)
st.title("Welcome to the ARNie interface!")
st.header("Select from the options to generate briefs")
st.write("Hello, my name is the Automated Routing Network planning system, \nbut you can call me ARNie.\n")

combo = st.file_uploader("Upload Site List 'Combined...'")
Ark = st.file_uploader("Upload Ark-image requests...")

st.write("Brief length, Week and Photographer/Brief number options: ")
	
briefLength = st.selectbox(
	"Please choose the maximum number of sites in each brief: ",
	("5", "10", "12", "15","20"),
	index=1,
	key = 'length',
)

weekN = st.selectbox(
	"Choose which week of the incharge you want: ",
	(1, 2),
	index=0,
	key = 'week',
)

location = st.selectbox(
	"Choose which location you want: ",
	('London', 'North West', 'Midlands', 'West', 'Yorkshire',
	'South and South-East', 'East Of England', 'Central Scotland', 'Border',
	'North East', 'Wales', 'South West','Grampian', 'HTV', 
	'Granada', 'Central', 'WCTV','North Scotland', 'Meridian', 'Anglia','Tyne Tees'),
	index=0,
	key = 'location',
)

greenlist = st.multiselect(
            "Select usable Sites Based on Standing Permits", 
            ('BLACKFRIARS','VICTORIA STN',"KING'S CROSS STN",
				'LIVERPOOL STREET STN','ST PANCRAS STN', 'WATERLOO STN',
				'BLUEWATER CENTRE - DARTFORD','WESTFIELD STRATFORD CITY',
				'WESTFIELD LONDON','INTU LAKESIDE S/C - THURROCK', 
				'INTU WATFORD S/C - WATFORD'),
)

st.write("Choose the number of briefs/photographers for each day: ")
checks = st.columns(7)
with checks[0]:
	mon ='Mon: '+st.selectbox('Mon',('0','1','2','3'),index=1,key='mon')
with checks[1]:
    tue ='Tue: '+st.selectbox('Tue',('0','1','2','3'),index=0,key='tue')
with checks[2]:
    wed ='Wed: '+st.selectbox('Wed',('0','1','2','3'),index=0,key='wed')
with checks[3]:
    thu ='Thu: '+st.selectbox('Thu',('0','1','2','3'),index=0,key='thu')
with checks[4]:
    fri ='Fri: '+st.selectbox('Fri',('0','1','2','3'),index=0,key='fri')
with checks[5]:
    sat ='Sat: '+st.selectbox('Sat',('0','1','2','3'),index=0,key='sat')
with checks[6]:
    sun ='Sun: '+st.selectbox('Sun',('0','1','2','3'),index=0,key='sun')


st.write("Your input (briefs): ",' '.join([mon,tue,wed,thu,fri,sat,sun]))
st.write(f'''\nThis will produce 
			{sum([int(mon[5:]),int(tue[5:]),int(wed[5:]),int(thu[5:]),int(fri[5:]),int(sat[5:]),int(sun[5:])])} 
			total briefs for week {weekN}, with {briefLength} 
			sites each. Sound good? (Press Submit)''')

choiceDigit = [int(mon[5:]),int(tue[5:]),int(wed[5:]),int(thu[5:]),int(fri[5:]),int(sat[5:]),int(sun[5:])]
brieflength = int(briefLength)-1
weekIndex = weekN

totDist = float(200)
maxDist = (totDist*1.757)/(brieflength+1)
		
def makeChart(chart_data):
	chart_data = chart_data.drop_duplicates(subset=['Postcode'])
	lat = chart_data.loc['A','Latitude']
	lon = chart_data.loc['A','Longitude']
	chart_data['Map Label']= list(chart_data.index.values)
	lenBrief = len(chart_data.index.values)
	chart_data.index.rename('Map',inplace=True)
	
	st.pydeck_chart(
		pdk.Deck(
			map_style='road',
			initial_view_state=pdk.ViewState(
				latitude=lat,
				longitude=lon,
				zoom=12,
				pitch=0,
			),
			layers=[
				pdk.Layer(
					"ScatterplotLayer",
					data=chart_data,
					id="Site-locations",
					get_position="[Longitude,Latitude]",
					filled=True,
					get_fill_color=[0,40,200],
					get_line_color = [0,0,0],
					pickable=True,
					auto_highlight=True,
					get_radius=100,
				),
				pdk.Layer(
					"TextLayer",
                    chart_data,
                    pickable=True,
                    get_position="[Longitude,Latitude]",
                    get_text="Map Label",
                    get_size=30,
                    get_color=[155, 155, 155],
                    get_angle=0,
                    get_text_anchor=String("middle"),
                    get_alignment_baseline=String("center"),
				),
			],tooltip={"text":"Map: {Map Label}, \nSite Number: {Site Number},\nBrands: {Brand}\nPost Code: {Postcode},\nAddress: {Address}"},
		)
	)
		
introtxt = '''
I am programmed to help you efficiently automate the process of planning briefs.\n 
By scanning the trillion trillion combinations of possible London briefs,
I can find the best combinations of routes and sites to generate optimal briefs that fit your specifications.'''
setuptxt = '''
Okay, to proceed, here is what I will need:\n 
(1) An .xlsx spreadsheet which containes the full incharge data (booked and non booked) in my directory\n
(2) All the bookingIds as provided by Ark as a csv, also in the same directory\n
(3) Five minutes of your time, :)\n
If these criteria are met, we are ready to proceed...'''

waiting = True
Arkdf = None

if st.button("Submit"):
	with st.spinner(text="Loading in incharge, please wait...  Step 1 / 3 "):
		
		print("starting imports")
		df_csv = pd.read_csv(Ark)
		BigBoy = pd.read_excel('https://github.com/FoxGodTodd/ARNie/raw/main/FrameIDLatLon.xlsx')
		dfx = pd.read_excel(combo)
		print("Done with Imports!")
		
		print('Cutting out stations and rail...')
		dfx = cutout.removeRailsMalls(greenlist,dfx)
		inchargeRef = df_csv['Incharge Ref'].to_numpy()[0]
		Arkdf = df_csv[['Booking Ref','Brand','Environment','Image Requests']]
		Arkdf.set_index('Booking Ref',inplace=True)
		print('We have Ark')
		waiting = False	
	LoadInchargeSuccess = st.success("Loaded!")
	Time.sleep(3)
else:
	Time.sleep(300)

if waiting:
	st.write('Waiting for submit...')

while Arkdf is None:
	waiting = True
	Time.sleep(60)

waiting = False	
Arkdf.index.rename('Booking Ref', inplace=True)

Bookingfilter = list(Arkdf.index.values) 

Weeks = dfx['mondayOfWeek'].unique()
Date = [Weeks[weekIndex-1]]

dayStarts = [] 
for y in range(0,12*len(choiceDigit),12):
	for j in range(choiceDigit[int(y/12)]):
		dayStarts.append(y)

Location = [str(location)]
result = dfx[dfx['mondayOfWeek'].isin(Date)&dfx['bookingRef'].isin(Bookingfilter)&dfx['tvArea'].isin(Location)]

result = BigBoyLayer(result,BigBoy)		

please = result[['bookingRef','furnIndex','address1','address2','address3','sizeCode','photoFileName','postCode','panelCode']]

df = result[['bookingRef','furnIndex','routeFrameID',
				'mondayOfWeek','bookedDaysOfWeek', 'startHour', 'endHour','latitude','longitude']]

totalUniqueBooks = Arkdf['Image Requests'].sum()
UniqueBooks = df['bookingRef'].unique()
uniques = Arkdf[Arkdf.index.isin(UniqueBooks)]
allShotsinWeek = uniques['Image Requests'].sum()
UniqueFrames = df['furnIndex'].unique()
print(f"There are {totalUniqueBooks} Unique Shots in the inCharge, and {allShotsinWeek} this week.")
print(f"Distributed across {len(UniqueFrames)} Unique Frames \n")

for day in week:
	df[day] = list(map(lambda x: x.count(day), df['bookedDaysOfWeek']))
	
dayweeks = []
for day in week:
	for T in slot:
		dayweeks.append(day+T)

df["T1"] = 1
df["T2"] = 1
df["T3"] = 1
df["T4"] = 1
df["T5"] = 1
df["T6"] = 1
df["T7"] = 1
df["T8"] = 1
df["T9"] = 1
df["T10"] = 1
df["T11"] = 1
df["T12"] = 1
 
start_series = df.loc[:,"endHour"]
for x in range(len(start_series)):
	startHour = df.loc[x,"startHour"]
	endHour = df.loc[x,"endHour"]
	if (startHour >= 10 or  endHour <= 9):
		df.loc[x,"T1"] = 0
	if (startHour >= 11 or  endHour <= 10):
		df.loc[x,"T2"] = 0
	if (startHour >= 12 or endHour <= 11):
		df.loc[x,"T3"] = 0
	if (startHour >= 13 or endHour <= 12):
		df.loc[x,"T4"] = 0
	if (startHour >= 14 or endHour <= 13):
		df.loc[x,"T5"] = 0
	if (startHour >= 15 or endHour <= 14):
		df.loc[x,"T6"] = 0
	if (startHour >= 16 or endHour <= 15):
		df.loc[x,"T7"] = 0
	if (startHour >= 17 or endHour <= 16):
		df.loc[x,"T8"] = 0
	if (startHour >= 18 or endHour <= 17):
		df.loc[x,"T9"] = 0
	if (startHour >= 19 or endHour <= 18):
		df.loc[x,"T10"] = 0
	if (startHour >= 20 or endHour <= 19):
		df.loc[x,"T11"] = 0
	if (startHour >= 21 or endHour <= 20):
		df.loc[x,"T12"] = 0
	
def progress_bar(current, total, bar_length=20):
	fraction = current / total
	arrow = int(fraction * bar_length - 1) * '=' + '>'
	padding = int(bar_length - len(arrow)) * ' '
	ending = '\n' if current == total else '\r'
	print(f'Progress: [{arrow}{padding}] {int(fraction*100)}%', end=ending)

def clock(currentTime,bookingsN, distance):
	#15.3 Minutes per k travelled
	#4 minutes per booking photographed
	#5 minutes for delays in travel
	#5 minutes delays in blurs
	#10 minutes check in for rail
	travelTime = 0
	addedTime = 5
	Dfactor = 1.183
	shootTime = 0
	averageV = 10
	add = False
	switch = False
	if(distance <= 1.5):
		averageV = 14
	elif(1.5< distance < 4):
		averageV = 10
	else:
		averageV = 8
	if currentTime <= 460:
		add = True
	travelTime = (averageV*Dfactor*distance)
	travelTime += 5
	for x in range(bookingsN):
		shootTime += 4
	if currentTime >= 500: 
		add = False
	addedTime = shootTime+travelTime+addedTime
	if((currentTime%60+addedTime)%60!=(currentTime%60+addedTime)):
		switch = True
	return(int(currentTime),add,switch,addedTime,travelTime)

def find_distance(coords1,coords2):
	km_distance = distance.distance(coords1,coords2,ellipsoid='Airy (1830)').km
	return(km_distance)

def calculate_rank(distance, bookingsN, bookings):
	priority = 0
	a = 1
	b = 1
	c = 1.5/(bookingsN+1)
	if distance != 0:
		rank = ((a*bookingsN)/(b*distance))+(c*priority)
	else:
		rank = a*bookingsN
	if distance > maxDist: rank = 0
	return(rank)
		
def doMainLoop(UniqueFrames,df):
	LoadInchargeSuccess.empty()
	dfNew = pd.DataFrame(index=UniqueFrames, columns=["MoT1"])
	dfTwo = pd.DataFrame(index=UniqueFrames, columns=["MoT1"])
	print("Starting initilization, Step 1 / 2")
	my_bar = st.progress(0, text="Starting initilization, Step 2 / 3")
	for i in range(7):
		progress_bar(i,6)
		my_bar.progress(int(100*(i/6)),text="Starting initilization, Step 2 / 3")
		for j in range(12):
			label = week[i]+"T"+str(j+1)
			largearray = []
			dftemp = df
			dftemp["newColumn"] = df[slot[j]]*df[week[i]]
			for index in UniqueFrames: 
				arraytemp = []
				dfSubset = dftemp[(dftemp["furnIndex"] == index)]	
				for entry in range(len(dfSubset["bookingRef"])):
					if (dfSubset.iloc[entry,28] == 1):
						arraytemp.append(str(dfSubset.iloc[entry,0]))
					else:
						arraytemp.append('_')
				uniques = np.unique(arraytemp)
				if '_' in uniques:
					arraytemp.insert(0,len(uniques)-1)
				else:
					arraytemp.insert(0,len(uniques))
				finalarray = np.array(np.unique(arraytemp))
				if (finalarray[len(finalarray)-1] == '_') and len(finalarray)>2:
					largearray.append(finalarray[:len(finalarray)-1])
				elif finalarray[1] != '_':
					largearray.append(finalarray)
				else:
					largearray.append([0])				
			dfNew[label] = (largearray)
			special_array = [element[0] for element in largearray]
			dfTwo[label] = np.array(special_array)
	Time.sleep(1)
	my_bar.empty()
	print("Finished intializing, starting next step \n")
	latitudearray = []
	longitudearray = []
	for frame in UniqueFrames:
		latitude = df[(df['furnIndex']==frame)]["latitude"].to_numpy()[0]
		longitude = df[(df['furnIndex']==frame)]["longitude"].to_numpy()[0]
		latitudearray.append(latitude)
		longitudearray.append(longitude)
	dfNew["latitude"] = latitudearray
	dfNew["longitude"] = longitudearray
	dfTwo["latitude"] = latitudearray
	dfTwo["longitude"] = longitudearray
	return(dfNew,dfTwo)


def removeOldBookings(dfNew,dfTwo,remove_array,first):
	for frame in UniqueFrames:
		for slot in dayweeks:
			target = dfNew.loc[frame,slot]
			for bookingRef in remove_array:
				if np.isin(bookingRef,target):
					if((int(Arkdf.at[bookingRef,"Image Requests"]) == 1) or ((int(Arkdf.at[bookingRef,"Image Requests"]) > 1) and frame==first)):
						array = np.delete(target,np.where(target==bookingRef))
						np.put(array,0,(str(int(array[0])-1)))
						dfNew.at[frame,slot] = array
						dfTwo.at[frame,slot] = str(int(dfTwo.loc[frame,slot])-1)
						target=array
	for bookingRef in remove_array:
		if(int(Arkdf.at[bookingRef,"Image Requests"]) > 1):
			Arkdf.at[bookingRef,"Image Requests"] = Arkdf.at[bookingRef,"Image Requests"]-1
		elif(int(Arkdf.at[bookingRef,"Image Requests"]) == 1):
			Arkdf.at[bookingRef,"Image Requests"] = 0
	return(dfNew,dfTwo)
	
def initialSort(dfNew,dfTwo,currentTime,slotIndex,loclist):
	rail = False
	timeSlot = dayweeks[slotIndex]
	dfTwo_sorted = dfTwo.sort_values(by=[timeSlot],ascending=False)
	picks = dfTwo_sorted.index[0:5]
	pickChoice = 1
	pick = picks[(pickChoice)-1]
	currentTime, add_test,switch_Test,addedtime,traveltime = clock(currentTime,int(dfTwo_sorted.at[pick,timeSlot]),0)
	currentTime += addedtime
	siteCoords = str(dfNew.loc[pick,'latitude'])+','+str(dfNew.loc[pick,'longitude'])
	brief.append(pick)
	loclist.append(siteCoords)
	if(str(dfNew.at[pick,timeSlot])!='0'):
		remove_array = (dfNew.loc[pick,timeSlot][1:])
		bookings = remove_array
		dfNew,dfTwo = removeOldBookings(dfNew,dfTwo,remove_array,pick)
		if(np.isin(bookings[0],Arkdf.index.values)):
			if(Arkdf.loc[bookings[0],"Environment"] == 'RAIL' or Arkdf.loc[bookings[0],"Environment"] == 'MALLS'):
				currentTime += 15
	else:
		bookings = ['none']	
	return(dfNew,dfTwo,brief,picks,currentTime,bookings,slotIndex,loclist)
	
def do_sorting(dfNew,dfTwo,brief,currentTime,slotIndex,initialIndex,loclist):
	currentSite = brief[-1]
	if(slotIndex<84):
		timeSlot = dayweeks[slotIndex]
	else:
		timeSlot = dayweeks[84]
	dfTwo_sorted = dfTwo.sort_values(by=[timeSlot],ascending=False)
	top = dfTwo_sorted.index[0:int(len(UniqueFrames)/10)]
	currentCoords = (dfNew.loc[currentSite,'latitude'],dfNew.loc[currentSite,'longitude'])
	rankings = []
	for site in top:
		tempslot = slotIndex
		siteCoords = str(dfNew.loc[site,'latitude'])+','+str(dfNew.loc[site,'longitude'])
		specialdist = find_distance(currentCoords,siteCoords)
		new_time, add_test,switch_test,addedtime,traveltime = clock(currentTime,int(dfTwo_sorted.at[site,timeSlot]),specialdist)	
		if(switch_test and tempslot<(initialIndex+11)):
			tempslot += 1
		if(tempslot<84):
			timeSlot = dayweeks[tempslot]	
			rank = calculate_rank(specialdist,int(dfTwo.loc[site,timeSlot]),dfNew.loc[site,timeSlot])
			dfTwo.at[site,'rank'] = rank
	dfTwo_sorted2 = dfTwo.sort_values(by=['rank'],ascending=False)
	new_site = dfTwo_sorted2.index[0]
	siteCoords = str(dfNew.loc[new_site,'latitude'])+','+str(dfNew.loc[new_site,'longitude'])
	new_dist = find_distance(currentCoords,siteCoords)
	if(slotIndex<84):
		if(slotIndex<(initialIndex+11)):
			timeSlot = dayweeks[slotIndex]	
	else:
		timeSlot = dayweeks[83]
	new_time, add_test,switch_test,addedTime,traveltime = clock(currentTime,int(dfTwo_sorted2.at[new_site,timeSlot]),new_dist)
	if(add_test):
		new_time = int(currentTime+addedTime)
		brief.append(new_site)
		loclist.append(siteCoords)
	if(switch_test and slotIndex<(initialIndex+11)):
		slotIndex += 1
	if(slotIndex<84 and slotIndex<(initialIndex+11)):
		timeSlot = dayweeks[slotIndex]
	else:
		timeSlot = dayweeks[83]
	if(str(dfNew.at[new_site,timeSlot])!='0'):
		remove_array = (dfNew.loc[new_site,timeSlot][1:])
		bookings = remove_array
		dfNew,dfTwo = removeOldBookings(dfNew,dfTwo_sorted2,remove_array,new_site)
		if((len(bookings) >= 1) and np.isin(bookings[0],Arkdf.index.values)):
			if(Arkdf.loc[bookings[0],"Environment"] == 'RAIL' or Arkdf.loc[bookings[0],"Environment"] == 'MALLS'):
				new_time += 15
	else:
		if (slotIndex<84 and slotIndex<(initialIndex+5)):
			slotIndex+=1
		bookings = ['none']
	return(dfNew,dfTwo,brief,new_time,slotIndex,bookings,loclist)

print("Starting Processing...")
dfNew, dfTwo = doMainLoop(UniqueFrames,df)

def quicktime(time,currentTime):
	minutes = time%60
	extra = ''
	if minutes < 10:
		extra = '0'
	currentTime.append(str(int((time-minutes)/60)+9)+':'+extra+str(int(minutes)))
	return(currentTime)

totalbookings=0
newbookings = []
print('Generating Briefs... Step 2 / 2 \n')
M = sum(choiceDigit)
InitializeSuccess = st.success("Finished intializing, starting next step \n")
Time.sleep(5)
InitializeSuccess.empty()
st.write('Generating Briefs... Step 3 / 3')
for i in range(M):
	bookingsList = []
	brands = []
	address = []
	postcodes = []
	Format = []
	Filenames = []
	brief = []
	loclist = []
	currentTime = ['9:00']
	time = 0
	dfTwo["rank"] = 0
	slotIndex = dayStarts[i]
	initialIndex = slotIndex
	print(f'\nBrief: {i+1}')
	print(weekfull[int(dayStarts[i]/12)])
	print(f'Progress: [>                   ] {1}%',end = '\r')
	st.header(f'Brief: {i+1}')
	my_bar = st.progress(0, text=f'Generating Brief {i+1}/{M}...')
	if(totalbookings<len(UniqueBooks)):
		dfNew,dfTwo,brief,picks,time,bookings,slotIndex,loclist = initialSort(dfNew,dfTwo,0,slotIndex,loclist)
		currentTime = quicktime(time,currentTime)
		bookingsList.append(bookings)
		while(time <= 460 and len(brief) <= brieflength and len(bookingsList[-1])!=0):
			progress_bar(len(brief),brieflength)
			my_bar.progress(int(100*(len(brief)/brieflength)),text=f'Generating Brief {i+1}/{M}...')
			dfNew,dfTwo,brief,time,slotIndex,bookings,loclist = do_sorting(dfNew,dfTwo,brief,time,slotIndex,initialIndex,loclist)
			currentTime = quicktime(time,currentTime)
			bookingsList.append(bookings)
			dfTwo["rank"] = 0
		my_bar.empty()
		print('\nHere is the full brief:')
		summy = 0
		for bookings in bookingsList:
			if(not(np.isin('none',bookings))):
				summy += len(bookings)
		print("Total bookings with this brief: \n", summy)
		ugh = len(np.unique(brief))
		st.write(f"We get {summy} shots from {ugh} sites with this brief")
		print("Sites visited: ", ugh)
		print(np.unique(brief))
		totalbookings+=summy
		for x in range(len(brief)):
			if(len(bookingsList[x])>=1):
				if(not(bookingsList[x][0] == 'none')):
					time = currentTime[x]
					print(time)
					print("Site (furnitureIndex): " ,brief[x]," at: "
							,loclist[x] ," Bookings Number:", len(bookingsList[x]))
					print('Bookings at site: ', bookingsList[x])
	else:
		print("\nFinished Processing")
		print("All bookings captured!")
	temp = []
	saveindex = 0
	for index, books in enumerate(bookingsList):
		temp+=[b for b in books if b != 'none']
	newbookings += temp
	betterbookings = [', '.join(x) for x in bookingsList]
	bestbookings = temp
	print('\nNew Shots: ', bestbookings)	
	tempB = []
	tempFN = []
	briefbig = []
	coordslist = []
	panelcodes = []
	latlist = []
	lonlist = []
	for index, bookings in enumerate(bookingsList):
		usable = please[(please["furnIndex"].eq(brief[index]))]
		usable = usable.drop_duplicates(subset='bookingRef',ignore_index=True) 
		usable.set_index("bookingRef",inplace=True)
		for b in bookings:
			coordslist.append(loclist[index])
			if((b != 'none') and (b in usable.index.values)):
				tempB.append(Arkdf.at[b,"Brand"])
				strib = usable.loc[b,'photoFileName']
				if(type(strib) is str):
					tempFN.append(strib)
				else:
					tempFN.append(strib.sample(n=1).to_numpy()[0])				
				if(type(usable.loc[b,"postCode"]) is not str):
					usable = usable[usable.index==b].sample(n=1)
				address.append((str(usable.at[b,"address1"])+', '+str(usable.at[b,"address2"])+', '+str(usable.at[b,"address3"])))
				Format.append(str(usable.at[b,"sizeCode"]))
				postcodes.append(str(usable.at[b,"postCode"]))
				panelcodes.append(str(usable.at[b,"panelCode"]))
			else:
				address.append(' ')
				panelcodes.append('1')
				Format.append(' ')
				postcodes.append(' ')
				tempB.append(' ')
				tempFN.append(' ')
			briefbig.append(brief[index])
	brands = tempB
	Filenames = tempFN
	branLength = len(bestbookings)
	coordslist = [str(coord).strip("()") for coord in coordslist]
	latlist = [float(coord[:coord.find(',')]) for coord in coordslist]
	lonlist = [float(coord[coord.find(',')+1:]) for coord in coordslist]
	notes = [' ']* branLength
	Media_owner = ['JCDecaux']*branLength
	Longarray = {"Brand":brands[:branLength],"Format":Format[:branLength],
					"Address":address[:branLength],"Coordinates":coordslist[:branLength],"Postcode":postcodes[:branLength],
					"File Name":Filenames[:branLength], "Notes":notes[:branLength],"Site Number":briefbig[:branLength],
					"Media Owner": Media_owner,"Panel Code": panelcodes[:branLength],"Booking IDs":bestbookings, "Latitude":latlist[:branLength], "Longitude":lonlist[:branLength]}
	print('Total shots so far: ',len(newbookings))
	dfFinal = pd.DataFrame(Longarray)
	postcode_to_letter = {postcode: letter for postcode, letter in zip(dfFinal['Postcode'].unique(), string.ascii_uppercase)}
	dfFinal['Map'] = dfFinal['Postcode'].map(postcode_to_letter)
	dfFinal = dfFinal[~dfFinal["Brand"].isin([' ','','NaN','none'])]
	Arkdf.index.names = ['Booking Ref']
	finalcols = dfFinal.columns.tolist()
	finalcols = finalcols[-1:] + finalcols[:-1]
	dfFinal = dfFinal[finalcols]
	dfFinal.set_index("Map",inplace=True)
	dfFinal2 = dfFinal[["Brand","Format","Address","Coordinates","Postcode","File Name", "Notes","Site Number","Media Owner","Panel Code","Booking IDs"]]
	st.dataframe(dfFinal2, use_container_width=True)
	makeChart(dfFinal[['Site Number','Address','Postcode','Brand','Latitude','Longitude']]) 

Arkdf = Arkdf[~Arkdf['Image Requests'].isin([0])]
print(f"Bookings captured: {totalbookings} out of {allShotsinWeek}")
st.header(f"Bookings captured: {totalbookings} out of {allShotsinWeek} this week, with {M} briefs.")
st.write("Download Remaining Image Requests for JCD campaigns")
st.dataframe(Arkdf, use_container_width=True)
final = np.array(newbookings)
final_size = len(np.unique(final))
print(np.unique(final), final_size)
check = True
if(int(final_size) != len(UniqueBooks)): check = False
print('Check we have all bookings: ', check)
percent = np.trunc(100*totalbookings/allShotsinWeek)
percenttotal = np.trunc(100*totalbookings/totalUniqueBooks)
print(f'We have {percent}% of bookings for this week.')
print(f'and we have {percenttotal}% of bookings for the whole incharge.')
