import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
import sqlite3
import folium
import time
import sys
import os

# ================================================================== #
#     Given an integer N, show (in a map) the N-most populous and    #
# 	  N-least populous neighborhoods with their population count.    #
# ================================================================== #
def popularityOfN(connection, iteration):
	
	limit = None
	while (limit == None or limit.isdigit() == False or int(limit) <= 0) :
		limit = input("Enter a number greater than 0: ")

	limit = int(limit)

	# Creating query that selects all neighbourhoods
	# - that have population greater than 0
	# - in descending order to obtain MoST N popular neighbourhoods
	topN = pd.read_sql("""SELECT DISTINCT p.Neighbourhood_Name, (CANADIAN_CITIZEN + NON_CANADIAN_CITIZEN + NO_RESPONSE) AS total 
						  FROM population p, coordinates c
						  WHERE p.Neighbourhood_name = c.Neighbourhood_name
						  AND Latitude <> 0 AND typeof(Latitude) = "real"
						  AND Longitude <> 0 AND typeof(Longitude) = "real"
						  AND total 
						  IN (
						  	SELECT DISTINCT (CANADIAN_CITIZEN + NON_CANADIAN_CITIZEN + NO_RESPONSE) AS total 
						  	FROM population p, coordinates c
							WHERE total > 0 
						  	AND Latitude <> 0 AND typeof(Latitude) = "real"
						  	AND Longitude <> 0 AND typeof(Longitude) = "real"
						  	AND p.Neighbourhood_name = c.Neighbourhood_name
						  	ORDER BY total DESC
						  	LIMIT {}
						  )ORDER BY total DESC;""".format(limit), connection)
	# print(topN)

	# Creating query that selects all neighbourhoods
	# - that have population greater than 0
	# - in ascending order to obtain LEAST N popular neighbourhoods
	botN = pd.read_sql("""SELECT DISTINCT p.Neighbourhood_Name, (CANADIAN_CITIZEN + NON_CANADIAN_CITIZEN + NO_RESPONSE) AS total 
						  FROM population p, coordinates c
						  WHERE p.Neighbourhood_name = c.Neighbourhood_name
						  AND Latitude <> 0 AND typeof(Latitude) = "real"
						  AND Longitude <> 0 AND typeof(Longitude) = "real"
						  AND total 
						  IN (
						  	SELECT DISTINCT (CANADIAN_CITIZEN + NON_CANADIAN_CITIZEN + NO_RESPONSE) AS total 
						  	FROM population p, coordinates c
							WHERE total > 0 
						  	AND Latitude <> 0 AND typeof(Latitude) = "real"
						  	AND Longitude <> 0 AND typeof(Longitude) = "real"
						  	AND p.Neighbourhood_name = c.Neighbourhood_name
						  	ORDER BY total 
						  	LIMIT {}
						  )ORDER BY total;""".format(limit), connection)

	# Converting pandas Dataframe into numpys array of arrays
	# and configuring for ties as well
	topN = determineTies(topN.values.tolist(), limit)
	botN = determineTies(botN.values.tolist(), limit)

	# Creating an array of arrays
	# - each inner array is the data set of the
	# - neighbourhood, coordinates, and populations
	# - top N MOST popular
	topStat = []
	for aName in range(0, len(topN)):
		location = pd.read_sql("""SELECT DISTINCT c.Neighbourhood_Name, Latitude, Longitude, (CANADIAN_CITIZEN + NON_CANADIAN_CITIZEN + NO_RESPONSE) AS total
								  FROM coordinates c, population p
								  WHERE c.Neighbourhood_Name = \"{}\"
								  AND p.Neighbourhood_Name = \"{}\"
								  AND total > 0;""".format(topN[aName][0], topN[aName][0]), connection)
		topStat.append(np.concatenate(location.values, axis = 0).tolist())

	# Creating an array of arrays
	# - each inner array is the data set of the
	# - neighbourhood, coordinates, and populations	
	# - bot N LEAST popular
	botStat = []
	for aName in range(0, len(botN)):
		location = pd.read_sql("""SELECT DISTINCT c.Neighbourhood_Name, Latitude, Longitude, (CANADIAN_CITIZEN + NON_CANADIAN_CITIZEN + NO_RESPONSE) AS total
								  FROM coordinates c, population p
								  WHERE c.Neighbourhood_Name = \"{}\"
								  AND p.Neighbourhood_Name = \"{}\"
								  AND total > 0;""".format(botN[aName][0], botN[aName][0]), connection)
		botStat.append(np.concatenate(location.values, axis = 0).tolist())

	# Plotting the statistics of top N and bottom N onto maps using folium
	edmonton = folium.Map(location = [53.5444, -113.4909], zoom_start = 11) 	# Hard coded edmonton's map coordinates

	for i in range(0, len(topStat)):
		folium.Circle(
			location = [topStat[i][1], topStat[i][2]],
			popup = "{} <br> {}".format(topStat[i][0], topStat[i][3]),
			radius = topStat[i][3] / 10,
			color = "blue",
			fill = True,
			fill_color = "crimson"
		).add_to(edmonton)

	for i in range(0, len(botStat)):
		folium.Circle(
			location = [botStat[i][1], botStat[i][2]],
			popup = "{} <br> {}".format(botStat[i][0], botStat[i][3]),
			radius = botStat[i][3],
			color = "green",
			fill = True,
			fill_color = "crimson"
		).add_to(edmonton)
			
	edmonton.save("N_TopBotPopulation-{}.html".format(iteration))
