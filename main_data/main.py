import userInterface as ui

import monthToCrimeCount as op1
import popularityOfN as op2
import findTopNCrimes as op3
import crimeFrequencyofN as op4

import sqlite3
import os.path
import time
import sys

def main():
	
	# Request for a valid database within the current directory
	dbFile = None
	while (not os.path.exists("./{}".format(dbFile))):
		try:
			dbFile = input("Please enter a valid database in the current directory (i.e. \"filename.db\"):  ")
		except:
			dbFile = input("There is no such database file in the directory, try again: ")
	connection = sqlite3.connect("./data/{}".format(dbFile))
	ui.clear()

	c2 = 0 
	c3 = 0 
	c4 = 0
	finish = False
	choice = None

	while finish != True:
		ui.displayOptions()
		while (choice == None or not choice.isdigit() or int(choice) not in range(1, 5)):
			choice = input("Choose desired task by entering its corresponding number on the left: ")

		if (choice == "1"):
			# ui.clear()
			op1.crimeOfYears(connection)
			time.sleep(1)

		elif (choice == "2"):
			# ui.clear()
			op2.popularityOfN(connection, c2)
			print("The file \"2-{}.html\" has been created and stored into the current directory.".format(c2))
			c2 += 1
			time.sleep(1.5)


		elif (choice == "3"):
			# ui.clear()
			op3.topCrimesOfN(connection, c3)
			print("The file \"3-{}.html\" has been created and stored into the current directory.".format(c3))
			c3 += 1
			time.sleep(1.5)

		elif (choice == "4"):
			op4.crimeToPopulation(connection, c4)
			print("The file \"4-{}.html\" has been created and stored into the current directory.".format(c4))
			c4 += 1
			time.sleep(1.5)


		elif (choice == "exit"):
			finish = True
			sys.exit()

		choice = ui.resetChoice(choice)
		ui.clear()

if __name__ == "__main__":	
	main()
