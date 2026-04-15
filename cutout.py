#Cut out malls and rail stations
import numpy as np
import pandas as pd

def removeRailsMalls(filterarray,dfTarget):

	filterStns = ['BLACKFRIARS','VICTORIA STN',"KING'S CROSS STN",
				'LIVERPOOL STREET STN','ST PANCRAS STN', 'WATERLOO STN']
	filterMalls = ['BLUEWATER CENTRE - DARTFORD','WESTFIELD STRATFORD CITY',
				'WESTFIELD LONDON','INTU LAKESIDE S/C - THURROCK', 
				'INTU WATFORD S/C - WATFORD']
	
	filterStns = []
	filterMalls = []
				
	filterboth = filterStns + filterMalls
	filterboth = filterarray	

	#dfTarget = pd.DataFrame(pd.read_excel(excel))
	dfNoMallRail = dfTarget[~dfTarget['businessAreaGroup'].isin(['MALLS','RAIL'])]
	dfMallRail = dfTarget[(dfTarget['businessAreaGroup'].isin(['RAIL'])&
					dfTarget['address1'].isin(filterboth) )| 
					(dfTarget['businessAreaGroup'].isin(['MALLS'])&
					dfTarget['address1'].isin(filterboth))]
	
	frames = [dfNoMallRail,dfMallRail]
	dfboth = pd.concat(frames)
	
	return(dfboth)					

array = ['BLACKFRIARS','VICTORIA STN',"KING'S CROSS STN",
				'LIVERPOOL STREET STN','ST PANCRAS STN', 'WATERLOO STN',
				'BLUEWATER CENTRE - DARTFORD','WESTFIELD STRATFORD CITY',
				'WESTFIELD LONDON','INTU LAKESIDE S/C - THURROCK', 
				'INTU WATFORD S/C - WATFORD']

