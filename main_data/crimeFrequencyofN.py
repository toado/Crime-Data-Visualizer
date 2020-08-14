
import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
import sqlite3
import folium
import time
import sys
import os

# =================================================================================== #
#     Given a range of years and an integer N, 										  #
#	  show (in a map) the Top-N neighborhoods with the 				 			      #
#     highest crimes to population ratio within the provided range.  			      #
#	  Also, show the most frequent crime type in each of these neighborhoods.         #
# =================================================================================== #
def crimeToPopulation(connection, iteration):


	# Creating a query of all years collected
	# - then converting the data frame into a list of 
	# - all available years 
	years = pd.read_sql("""SELECT DISTINCT Year
						   FROM crime_incidents
						   WHERE typeof(Year) = "integer"
	  					   ORDER BY Year;""", connection)
	years = np.concatenate(years.values, axis = 0).tolist()

	# Query of all neighbourhoods
	nbhoods = pd.read_sql("""SELECT DISTINCT ci.Neighbourhood_Name
							 FROM crime_incidents ci, coordinates c
							 WHERE typeof(Month) = "integer"
							 AND ci.Neighbourhood_Name = c.Neighbourhood_Name
							 AND Latitude <> 0 
							 AND Longitude <> 0
							 ORDER BY ci.Neighbourhood_Name;""", connection)
	nbhoods = np.concatenate(nbhoods.values, axis = 0)
	

	# request user inputs, returns 3 inputs
	inputs = q4inputs(years, nbhoods)
	start = int(inputs[0])
	end = int(inputs[1])
	limit = int(inputs[2])

	# Query that finds the ratio between crime count : population
	ratio = pd.read_sql("""SELECT DISTINCT pc.Neighbourhood_Name, (cc.crime_count * 1.0 / pc.ppl_count) as ratio
								FROM (SELECT DISTINCT ci.Neighbourhood_Name, SUM(Incidents_count) as crime_count
									  FROM coordinates c, crime_incidents ci
									  WHERE Latitude <> 0.0 AND typeof(Latitude) = "real"
									  AND Longitude <> 0.0 AND typeof(Longitude) = "real"
									  AND ci.Neighbourhood_Name <> "Not Entered"
									  AND ci.Neighbourhood_Name = c.Neighbourhood_Name
									  AND ci.Year BETWEEN {} AND {}
									  GROUP BY ci.Neighbourhood_Name) cc,

									  (SELECT distinct p.Neighbourhood_Name, (CANADIAN_CITIZEN + NON_CANADIAN_CITIZEN + NO_RESPONSE) as ppl_count
									   FROM population p, coordinates c
									   WHERE ppl_count > 0 
									   AND Latitude <> 0.0 AND typeof(Latitude) = "real"
									   AND Longitude <> 0.0 AND typeof(Longitude) = "real"
									   AND c.Neighbourhood_Name = p.Neighbourhood_Name
									   AND c.Neighbourhood_Name <> "Not Entered") pc
								WHERE cc.Neighbourhood_Name = pc.Neighbourhood_Name
								AND ratio 
								IN (SELECT (cc.crime_count * 1.0 / pc.ppl_count) as ratio
									FROM (SELECT DISTINCT ci.Neighbourhood_Name, SUM(Incidents_count) as crime_count
										  FROM coordinates c, crime_incidents ci
									  	  WHERE Latitude <> 0.0 AND typeof(Latitude) = "real"
									  	  AND Longitude <> 0.0 AND typeof(Longitude) = "real"
									  	  AND ci.Neighbourhood_Name <> "Not Entered"
									      AND ci.Neighbourhood_Name = c.Neighbourhood_Name
									  	  AND ci.Year BETWEEN {} AND {}
									  	  GROUP BY ci.Neighbourhood_Name) cc,

										 (SELECT distinct p.Neighbourhood_Name, (CANADIAN_CITIZEN + NON_CANADIAN_CITIZEN + NO_RESPONSE) as ppl_count
										  FROM population p, coordinates c
									   	  WHERE ppl_count > 0 
									   	  AND Latitude <> 0.0 AND typeof(Latitude) = "real"
									   	  AND Longitude <> 0.0 AND typeof(Longitude) = "real"
									   	  AND c.Neighbourhood_Name = p.Neighbourhood_Name
									   	  AND c.Neighbourhood_Name <> "Not Entered") pc
									WHERE cc.Neighbourhood_Name = pc.Neighbourhood_Name
									GROUP BY cc.Neighbourhood_Name
									ORDER BY ratio DESC
									LIMIT {})
								ORDER BY ratio DESC;""".format(start, end, start, end, limit), connection)

	ratio = determineTies(ratio.values.tolist(), limit)

	# A query to find the most frequent crime type
	# then append that crime type to the list of ratios
	for i in range(0, len(ratio)):
		df_freqCrime = pd.read_sql_query("""SELECT Neighbourhood_Name, Crime_Type, MAX(count) as crimeCount
	                                    	FROM (SELECT ci.Neighbourhood_Name, ci.Crime_Type, SUM(Incidents_Count) as count
	                                        	  FROM crime_incidents ci, coordinates c
	                                     	      WHERE ci.Year BETWEEN %d AND %d
	                                          	  AND Latitude <> 0.0 and Latitude <> "Not Entered"
	                                         	  AND Longitude <> 0.0 and Longitude <> "Not Entered"
	                                         	  AND ci.Neighbourhood_Name = "%s"
	                                          	  AND ci.Neighbourhood_Name = c.Neighbourhood_Name                    
	                                          	  GROUP BY ci.Neighbourhood_Name, ci.Crime_Type)
	                                    	GROUP BY Neighbourhood_Name
	                                    	HAVING MAX(count)
	                                    	IN
	                                    	   (SELECT MAX(counts)
	                                    		FROM (SELECT ci.Neighbourhood_Name, ci.Crime_Type, SUM(Incidents_Count) as counts
	                                        	 	  FROM crime_incidents ci, coordinates c
	                                     	      	  WHERE ci.Year BETWEEN %d AND %d
	                                          	  	  AND Latitude <> 0.0 and Latitude <> "Not Entered"
	                                         	  	  AND Longitude <> 0.0 and Longitude <> "Not Entered"
	                                         	  	  AND ci.Neighbourhood_Name = "%s"
	                                          	  	  AND ci.Neighbourhood_Name = c.Neighbourhood_Name
	                                          	  	  GROUP BY ci.Neighbourhood_Name, ci.Crime_Type)
	                                    		GROUP BY Neighbourhood_Name
	                                    		ORDER BY MAX(counts) DESC)
	                                    	ORDER BY MAX(count) DESC;"""%(start, end, ratio[i][0], start, end, ratio[i][0]), connection)
		ratio[i].append(np.concatenate(df_freqCrime.values, axis = 0).tolist()[1])


	# Finding the coordinates of each location
	for i in range(0, len(ratio)):
		location = pd.read_sql("""SELECT Neighbourhood_Name, Latitude, Longitude
								  FROM coordinates c
								  WHERE Neighbourhood_Name = \"%s\";""" %(ratio[i][0]), connection)

		coords = np.concatenate(location.values, axis = 0).tolist()
		ratio[i].append(coords[1])
		ratio[i].append(coords[2])

	# Plotting the statistics of top N and bottom N onto maps using folium
	edmonton = folium.Map(location = [53.5444, -113.4909], zoom_start = 11) 	# Hard coded edmonton's map coordinates

	for i in range(0, len(ratio)):
		folium.Circle(
			location = [ratio[i][3], ratio[i][4]],
			popup = "{} <br> {} <br> {}".format(ratio[i][0], ratio[i][2], ratio[i][1]),
			radius = ratio[i][1] * 300,
			color = "blue",
			fill = True,
			fill_color = "crimson"
		).add_to(edmonton)

	edmonton.save("Q4-{}.html".format(iteration))
	# os.system("google-chrome Q4-{}.html".format(iteration))


# ----------------------------------------------------------------------------- #
# For task 4, function is to request for user inputs for desired data output    #
# Function used to make program look less cluttered		   					    #
# ----------------------------------------------------------------------------- #
def q4inputs(years, nbhoods):

	startYr = None
	while (startYr == None or not startYr.isdigit() or int(startYr) < years[0] or int(startYr) > years[len(years) - 1]):	# Request user to enter start year from given range
		startYr = input("Enter a start year from {} - {} (inclusive): ".format(years[0], years[len(years) - 1]))

	endYr = None
	while (endYr == None or not endYr.isdigit() or int(endYr) < int(startYr) or int(endYr) > years[len(years) - 1]):		# Request user to enter end year from chosen start year to end of range
		endYr = input("Enter an end year from {} - {} (inclusive): ".format(startYr, years[len(years) - 1]))

	# Request user to 
	numNbhoods = None
	while (numNbhoods == None or not numNbhoods.isdigit() or int(numNbhoods) <= 0 or int(numNbhoods) > len(nbhoods)):
		numNbhoods = input("Enter a number of neighborhoods: ")

	return startYr, endYr, numNbhoods



# ----------------------------------------------------------------------------- #
# For to determine whether ties are present or not,   						    #
# and it will configure the output with it considered   					    #
# ----------------------------------------------------------------------------- #
def determineTies(array, limit):

	tieList = []
	# if no ties
	if (len(array) <= limit):
		for i in range(0, len(array)):
			tieList.append(array[i])

	# tie exists
	elif (array[limit][1] == array[limit - 1][1]):
		for i in range(0, limit + 1):
			tieList.append(array[i])

	return tieList
