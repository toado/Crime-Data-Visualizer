import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
import sqlite3
import folium
import time
import sys
import os

# Displays bar plot of (Time, month-wise, to count of desired crime type)
def crimeOfYears(connection):		

	# Creating a query of all years collected
	# - then converting the data frame into a list of 
	# - all available years 
	df_years = pd.read_sql_query("""SELECT DISTINCT Year
	                                FROM crime_incidents
	                                WHERE typeof(Year) = "integer"
	                                ORDER BY Year;""", connection)
	years = np.concatenate(df_years.values,axis = 0).tolist()

	# Query of all crime types
	df_crimeType = pd.read_sql_query("""SELECT DISTINCT Crime_Type
	                                    FROM crime_incidents
	                                    WHERE typeof(Month) = "integer"
	                                    ORDER BY Crime_Type;""", connection)
	crimeType = np.concatenate(df_crimeType.values, axis = 0).tolist()

	returns = inputs(years, crimeType)
	start = returns[0]
	end = returns[1]
	crime = returns[2]

	# Query obtaining sum of crimes happening per month within a range of years
	# filters out locations without coordinates -- means location DNE
	df_allCrimes = pd.read_sql_query("""SELECT Month, SUM(ci.Incidents_Count) as Count
	                                    FROM crime_incidents ci, coordinates c
	                                    WHERE ci.Crime_Type = "%s" 
	                                    AND ci.Year BETWEEN %d AND %d
	                                    AND ci.Neighbourhood_Name = c.Neighbourhood_Name
	                                    AND c.Latitude <> 0.0 and typeof(c.Latitude) = "real"
	                                    AND c.Longitude <> 0.0 and typeof(c.Longitude) = "real" 
	                                    GROUP BY Month;"""%(crime, int(start), int(end)), connection)
	allCrimes = df_allCrimes.values

	# creating list of all months used for checking later
	months = [0] * 12
	for i in range(0, 12):
	    months[i] = i + 1

	# From the query, if a month is not present
	# add into dataframe to plot the month of 0 Incidents_Count
	if len(allCrimes) != len(months):
	        # Obtaining months that are present from the query
	        dataMonths = [0] * len(allCrimes)
	        for i in range(0, len(allCrimes)):
	            dataMonths[i] = allCrimes[i][0]

	        missing = list(set(months) - set(dataMonths)) # Finding which months have 0 Incidents_Count

	        # Insert missing month and its 0 Incidents_Count back Incidents_Count
	        # numpy array of the query's dataframe
	        for i in range(0, len(missing)):
	            npIndex = missing[i] - 1
	            mValue = [missing[i], 0]
	            allCrimes = np.insert(allCrimes, npIndex, mValue, axis = 0)

	        # Reconstructing query dataframe to include months with 0 Incidents_Count
	        df_allCrimes = pd.DataFrame(allCrimes, columns =["Month", "Count"])

	bar_plot = df_allCrimes.plot.bar(x = "Month")
	plt.plot()
	plt.show()

def inputs(years, crimeTypes):

	startYr = None
	while (startYr == None or not startYr.isdigit() or int(startYr) < years[0] or int(startYr) > years[len(years) - 1]):	# Request user to enter start year from given range
		startYr = input("Enter a start year from {} - {} (inclusive): ".format(years[0], years[len(years) - 1]))

	endYr = None
	while (endYr == None or not endYr.isdigit() or int(endYr) < int(startYr) or int(endYr) > years[len(years) - 1]):		# Request user to enter end year from chosen start year to end of range
		endYr = input("Enter an end year from {} - {} (inclusive): ".format(startYr, years[len(years) - 1]))

	# Display available crime types 
	print("\nCrime Type List:")
	for i in range(0, len(crimeTypes)):
		print("  - {}".format(crimeTypes[i]))
		if (i == len(crimeTypes) - 1):
			print("\n")

	# Request user to choose a crime type
	crimePick = None
	while (crimePick == None or crimePick not in crimeTypes):
		crimePick = input("Enter a crime type (CASE SENSITIVE): ")
	# print(crimePick)

	return startYr, endYr, crimePick
