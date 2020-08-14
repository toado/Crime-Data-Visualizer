import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
import sqlite3
import folium
import time
import sys
import os

# ===================================================================== #
#     Given a range of years, a crime type and an integer N,            #
#     show (in a map) the Top-N neighborhoods and their crime count     #
#     where the given crime type occurred most within the given range.  #
# ===================================================================== #
def topCrimesOfN(connection, iteration):

	# Creating a query of all years collected
	# - then converting the data frame into a list of 
	# - all available years 
	years = pd.read_sql("""SELECT DISTINCT Year
						   FROM crime_incidents
						   WHERE typeof(Year) = "integer"
	  					   ORDER BY Year;""", connection)
	years = np.concatenate(years.values, axis = 0).tolist()

	# Query of all crime types
	crimeTypes = pd.read_sql("""SELECT DISTINCT Crime_Type
								FROM crime_incidents
								WHERE typeof(Month) = "integer"
								ORDER BY Crime_Type;""", connection)
	crimeTypes = np.concatenate(crimeTypes.values, axis = 0).tolist()

	# Query of all neighbourhoods
	nbhoods = pd.read_sql("""SELECT DISTINCT ci.Neighbourhood_Name
							 FROM crime_incidents ci, coordinates c
							 WHERE typeof(Month) = "integer"
							 AND ci.Neighbourhood_Name = c.Neighbourhood_Name
							 AND Latitude <> 0 AND typeof(Latitude) = "real"
							 AND Longitude <> 0 AND typeof(Longitude) = "real"
							 ORDER BY ci.Neighbourhood_Name;""", connection)
	nbhoods = np.concatenate(nbhoods.values, axis = 0)

	inputs_ = inputs(years, crimeTypes, nbhoods)	# Return 4 inputs
	startYr = inputs[0] 
	endYr = inputs[1]
	crime = inputs[2]
	numHoods = int(inputs[3])


	# Query of neighbourhoods with highest counts of a specific crime
	crimeCounts = pd.read_sql("""SELECT ci.Neighbourhood_Name, SUM(Incidents_Count)
						   		 FROM crime_incidents ci, coordinates c
						   		 WHERE Crime_Type = "{}"
						   		 AND Year BETWEEN {} AND {}
						   		 AND ci.Neighbourhood_Name <> "Not Entered" 
						   		 AND ci.Neighbourhood_Name = c.Neighbourhood_Name
						   		 AND Latitude <> 0 AND typeof(Latitude) = "real"
						   		 AND Longitude <> 0 AND typeof(Longitude) = "real"
						  		 GROUP BY ci.Neighbourhood_Name
						   		 HAVING SUM(Incidents_Count)	
						   		 IN 
						   		 	(SELECT SUM(Incidents_Count)
						    		 FROM crime_incidents ci, coordinates c
						     		 WHERE Crime_Type = "{}"
						     		 AND Year BETWEEN {} AND {}
						     		 AND ci.Neighbourhood_Name <> "Not Entered" 
						     		 AND ci.Neighbourhood_Name = c.Neighbourhood_Name
						     		 AND Latitude <> 0 AND typeof(Latitude) = "real"
						     		 AND Longitude <> 0 AND typeof(Longitude) = "real"
						     		 GROUP BY ci.Neighbourhood_Name
						     		 ORDER BY SUM(Incidents_Count) DESC
						     		 LIMIT {})
						   		 ORDER BY SUM(Incidents_Count) DESC;""".format(crime, startYr, endYr, crime, startYr, endYr, numHoods), connection)
	# Convert dataframe into a list 
	# Then create a final list with ties taken into consideration
	crimeCounts = determineTies(crimeCounts.values.tolist(), numHoods)

	# Obtaining the coordinates of each location that was outputted
	# - from the query above
	coords = []
	for i in range(0, len(crimeCounts)):
		location = pd.read_sql("""SELECT Neighbourhood_Name, Latitude, Longitude
							      FROM coordinates 
							      WHERE Neighbourhood_Name = \"{}\";""".format(crimeCounts[i][0]), connection)
		coords.append(np.concatenate(location.values, axis = 0).tolist())
		coords[i].append(crimeCounts[i][1])


	# Plotting the statistics of top N and bottom N onto maps using folium
	edmonton = folium.Map(location = [53.5444, -113.4909], zoom_start = 11) 	# Hard coded edmonton's map coordinates
	radiusSizing3(edmonton, crime, coords, iteration)

def inputs(years, crimeTypes, nbhoods):

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

	# Request user to 
	numNbhoods = None
	while (numNbhoods == None or not numNbhoods.isdigit() or int(numNbhoods) <= 0 or int(numNbhoods) > len(nbhoods)):
		numNbhoods = input("Enter a number of neighborhoods: ")

	return startYr, endYr, crimePick, numNbhoods

# Function to appropriate the higlighled circle's size (radius)
def radiusSizing3(edmonton, crime, coords, iteration):
	for i in range(0, len(coords)):
		if (crime == "Theft Over $5000"):
			folium.Circle(
				location = [coords[i][1], coords[i][2]],
				popup = "{} <br> {}".format(coords[i][0], coords[i][3]),
				radius = coords[i][3] * 35,
				color = "blue",
				fill = True,
				fill_color = "crimson"
				).add_to(edmonton)

		elif (crime == "Theft Of Vehicle"):
			folium.Circle(
				location = [coords[i][1], coords[i][2]],
				popup = "{} <br> {}".format(coords[i][0], coords[i][3]),
				radius = coords[i][3] * 2,
				color = "blue",
				fill = True,
				fill_color = "crimson"
				).add_to(edmonton)

		elif (crime == "Robbery"):
			folium.Circle(
				location = [coords[i][1], coords[i][2]],
				popup = "{} <br> {}".format(coords[i][0], coords[i][3]),
				radius = coords[i][3] * 3,
				color = "blue",
				fill = True,
				fill_color = "crimson"
				).add_to(edmonton)

		elif (crime == "Sexual Assaults"):
			folium.Circle(
				location = [coords[i][1], coords[i][2]],
				popup = "{} <br> {}".format(coords[i][0], coords[i][3]),
				radius = coords[i][3] * 6,
				color = "blue",
				fill = True,
				fill_color = "crimson"
				).add_to(edmonton)

		elif (crime == "Homicide"):
			folium.Circle(
				location = [coords[i][1], coords[i][2]],
				popup = "{} <br> {}".format(coords[i][0], coords[i][3]),
				radius = coords[i][3] * 100,
				color = "blue",
				fill = True,
				fill_color = "crimson"
				).add_to(edmonton)		

		else:
			folium.Circle(
				location = [coords[i][1], coords[i][2]],
				popup = "{} <br> {}".format(coords[i][0], coords[i][3]),
				radius = coords[i][3],
				color = "blue",
				fill = True,
				fill_color = "crimson"
				).add_to(edmonton)

	edmonton.save("TopN-{}.html".format(iteration))
