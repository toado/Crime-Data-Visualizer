User Guide

In order to run our application on the command line, the user should type “ python3 main.py ”

When the application runs, the user will be prompted to enter a database file with the format
“aDatabase.db” where “aDatabase” is the database file that the user wants the application to read
from (NOTE: the database file must be within the same current directory) . Once the application
connects to the database file, the user will be met with the main menu where they can select any of
the displayed option by inputting any number from 1 - 4 or they can exit the program.

The foundation of this program is the main menu and then the user is prompted to choose an
option from one of the 4 main functions of the program;

1. Statistic of Crime Given Range of Years
2. Popularity of Top N and Bottom N Neighbourhoods
3. Top N Neighbourhoods of Crime Type Given Range of Years
4. Top N Neighbourhoods of Highest Crime to Population Ratio

* NOTE : at the end of each execution of a selected option, an html file will created and store
into the current directory 

If the user selects the first option then the user will have to input the start year, end year and
type of crime. Afterwards a bar chart is displayed from the created query with the months (from 1 to
12 ) labelled on the x-axis and the count representing the total number of incidents being on the
y-axis. If there is an instance where no incidents occurred in a particular month for the crime type,
the bar chart will still display the month having a count of zero. The screen will clear once an option
is executed and the main menu will be presented again where the user is prompted to choose a new
option.

Selecting the second option, the user will have to input an integer greater than zero. Upon
entering the integer, a html file will be created through Folium. This file is a map representation of
the top N most populated neighbourhoods and the Top N least populated neighborhoods. The
circles on the map from the html file will display neighborhoods name and population count when
clicked on. If there was an instance of a tie, then it will display the Top N +1 and/or bottom N + 1
neighbourhoods depending on where ties are present. The blue outlined circles represent the top
N (+1) most populated neighbourhoods and the green outlined circles represent the top N (+1)
least populated neighbourhoods. The screen will clear once an option is executed and the main
menu will be presented again where the user is prompted to choose a new option.

The third option will need the user to input a start year, end year, type of crime and number
of neighbourhoods. After the last input, a html file will be generated through Folium which represents
a map displaying the top neighbourhoods based on user input of range of years and crime type. The
blue outlined circles on the map will display the neighbourhood name as well as the crime count of
the specified crime type within the range of years when clicked on. If there was an instance of a tie,
then it will display the Top N +1 and/or bottom N + 1 neighbourhoods depending on where ties are
present. The screen will clear once an option is executed and the main menu will be presented again
where the user is prompted to choose a new option.

Finally the fourth option, the user will be prompted to input the start year, end year and the
number of neighborhoods. A html file will be created through the use of Folium to display a map of
the top N neighbourhoods with the highest crimes to population ratio as well as the most frequent
crime type. The blue outlined circles on the map will display the neighbourhood name, type of crime
as well as the ratio of crime to population count when clicked on. The screen will clear once an
option is executed and the main menu will be presented again where the user is prompted to choose
a new option.

With each execution of each option, it will produce a new html file with a count that is in
correspondence with the number of times that specific option is executed. Another note, the border
of the circles that are produced are going to be colored blue as its contrast to the map will help
locate the data produced easier.

If the user enters “exit” while on the main menu, then the program will finish and exit out.
After selecting any option on the main menu and finishing any of the selected functions, the screen
will always clear after being prompted to input “Enter” for a clean UI experience.