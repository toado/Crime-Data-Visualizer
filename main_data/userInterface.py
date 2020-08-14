import os

# Draw Menu Borders
def drawContent():
  print("/" + "*" * 75 + "/")

# display possible actions
def displayOptions():
  drawContent()
  print(" There are 4 available options, please select one to proceed further;\n" \
      " otherwise, type \"exit\" to exit the program.\n\n",
      "  1. Statistic of Crimes Given Range of Years\n",
      "  2. Popularity of Top N and Bottom N Neighborhoods\n",
      "  3. Top N Neighborhoods of Crime Type Given Range of Years\n",
      "  4. Top N Neighborhoods of Highest Crime to Population Ratio\n")
  drawContent()
  print("\n")


# clear terminal for clean ui
def clear():
  # input("Press the \"Enter\" to continue\n")
  os.system('clear')


def resetChoice(choice):
  choice = None
  return choice

