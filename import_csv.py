# ---------------
# name:     import_csv.py
# author:   apa
# created:  2018-10-13
# descr.:   converts input csv into lists
# log:      2018-10-13 / apa / first draft to use a location, with a settings and a optional parameter list
#           2018-10-14 / apa / implemented further checkings
# --------------
# clear possible legacy variable assignments
# for vars in dir():
#    if ("__" not in vars ):
#        print (vars)
#        del vars

# modules
import sys
from datetime import datetime
import os
import csv

# ---------------------------------------------------------------------------------------------------
# ########## IMPORT VARIABLES #############

# myDir = os.path.dirname(sys.argv[0])
# settingsFileName = "settings.txt"
# settingsPath = myDir + "/" + settingsFileName
settingsDelimiter = "|"
settingsPath = "C:/Users/Anja/PycharmProjects/spos/settings.txt"

# check the settings file exists
if os.path.isfile(settingsPath) is False:
    sys.exit("Please check the file '%s' exists." % settingsPath)

# read the content of the settings file
settingsFile = open(settingsPath, 'r')
settingsList = settingsFile.readlines()
lines = 0
lines = len(settingsList)

if lines == 0:
    sys.exit("Please check the settings file no settings could be found.")

# ----------
# assign the settings to the variables
for line in range(0, lines):
    settingParam = settingsList[line].split(settingsDelimiter)[0].strip()
    if settingParam == "workDir":
        workDir = settingsList[line].split(settingsDelimiter)[1].strip()
    elif settingParam == "inputFileName":
        inputFileName = settingsList[line].split(settingsDelimiter)[1].strip()
    elif settingParam == "csvDelimiter":
        csvDelimiter = settingsList[line].split(settingsDelimiter)[1].strip()
    elif settingParam == "colNames":
        colNames = settingsList[line].split(settingsDelimiter)[1].strip()
        colList = colNames.split(",")
    elif settingParam == "decDelimiter":
        decDelimiter = settingsList[line].split(settingsDelimiter)[1].strip()
    elif settingParam == "coordForm":
        coordForm = settingsList[line].split(settingsDelimiter)[1].strip()
    elif settingParam == "timeFormat":
        timeFormat = settingsList[line].split(settingsDelimiter)[1].strip()

# -------------
# check all variables are available
# check the working directory exist
if os.path.isdir(workDir) is False:
    sys.exit("Please check the dir '%s' exists." % (workDir))

# check the file with the location list exists
inputFilePath = workDir + inputFileName
if os.path.isfile(inputFilePath) is False:
    sys.exit("Please check the dir '%s' exists." % (workDir))

# check delimiter is not empty

# check column names

# check time format

print(settingsList)

# --------------------------------------------------------------------------------------------
#        READ NMB PARAMETER LIST

parameterFileNameInd = "param"
parameterExtension = ".txt"

# check ONE parameter list exists
checkCount = 0
for file in os.listdir(workDir):
    if file.endswith(parameterExtension):
        if file.startswith(parameterFileNameInd):
            checkCount = checkCount + 1
            parameterFileName = file

if checkCount == 0:
    print("No customparameter list is defined. All parameter will be extracted")
elif checkCount > 1:
    sys.exit("Please check only the parameter list to be used starts with 'param'.")
elif checkCount == 1:
    # read the content of the parameter list
    parameterPath = workDir + parameterFileName
    parameterFile = open(parameterPath, 'r')
    parameterList = parameterFile.readlines()
    lines = 0
    lines = len(parameterList)

if lines == 0:
    sys.exit("Please check the parameter list in the work directory.")

parameter = str(parameterList[0]).strip()
print(parameter)
# ---------------------------------------------------------------------------------------------
#      READ SHIP POSITION LIST

# read the content of the csv into a dictionary
with open(inputFilePath) as csvFile:
    csvTable = csv.DictReader(csvFile, delimiter=csvDelimiter)
    for row in csvTable:
        nPosition = int(row[colList[0]])
        # ------
        # check the coordinates are provided in the defined settings - decimal degree
        try:
            latPosition = float(row[colList[1]])
        except ValueError:
            sys.exit("That was no coordinate in decimal degree: %s. Please correct the positions file _"
                     "or change the settings" % (row[colList[1]]))
        try:
            lonPosition = float(row[colList[2]])
        except ValueError:
            sys.exit("That was no coordinate in decimal degree: %s. Please correct the positions file _"
                     "or change the settings" % (row[colList[2]]))

        # ------
        # check for the input time format
        try:
            timePosition = datetime.strptime(str(row[colList[3]]), timeFormat)
        except ValueError:
            sys.exit("That was no valid date: %s. Please correct the positions file _"
                     "or change the date-time-format in the settings" % (row[colList[3]]))

        # ------
        # check the values are reasonable
        timeNow = datetime.now()
        if timeNow < timePosition:
            sys.exit("Please check the DATE value for position %i: %s. _"
                     "It is in the future." % (nPosition, timePosition))
        if int(round(latPosition, 0)) not in range(-90, 90, 1):
            sys.exit("Please check the LATitude value for position %i: %F." % (nPosition, latPosition))
        if int(round(lonPosition, 0)) not in range(-180, 180, 1):
            sys.exit("Please check the LONitude value for position %i: %f." % (nPosition, lonPosition))

print(latPosition)
print(lonPosition)
print(timePosition)


# --------------------------------------------------------------------------------------------------------------------
#     TIME FORMAT CONVERSION

# check the given date time format and converts them into the required if necessary
def checkTimeFormat(dateTimeString):
    # 1)  2018-10-01 17:00          %Y-%m-%d %H:%M
    # 2)  2018-10-01 17:00:00       %Y-%m-%d %H:%M:$S
    # 3)  10-01-2018 17:00          %d-%m-%Y %H:%M
    # 4)  10-01-2018 17:00:00       %d-%m-%Y %H:%M:$S
    # 5)  01.09.2018 17:00          %d.%m.%Y %H:%M
    # 6)  01.09.2018 17:00:00       %d.%m.%Y %H:%M:$S
    # 7)  01.09.18 17:00            %d.%m.%Y %H:%M
    # 8)  01.09.18 17:00:00         %d.%m.%Y %H:%M:$S
    # 9)  1.9.2018 17:00            %d.%m.%y %H:%M      ?
    # 10) 1.9.2018 17:00:00         %d.%m.%y %H:%M:$S   ?
    # 11) 2018/10/01 17:00          %Y/%m/%d %H:%M
    # 12) 2018/10/01 17:00:00       %Y/%m/%d %H:%M:$S
    # 13) 01/10/2018 17:00          %d/%m/%Y %H:%M
    # 14) 01/10/2018 17:00:00       %d/%m/%Y %H:%M:$S
    # 15) 01/10/18 17:00            %d/%m/%y %H:%M
    # 16) 01/10/18 17:00:00         %d/%m/%y %H:%M:$S
    # 17) 2018/01/10 17:00          %Y/%d/%m %H:%M      ??????
    # 18) 2018/01/10 17:00:00       %Y/%d-%m %H:%M:$S

    try:
        x = int(raw_input("Please enter a number: "))
    except ValueError:
        print
        "Oops!  That was no valid date.  Try again..."

    return(defaultDateTime)


# --------------------------------------------------------------------------------------------------------------------
#       COORDINATES FORMAT CONVERSION

# checks the format of the given coordinates and converts them if necessary into decimal degree if necessary
def checkCoordDD(coord):
    # check for degree sign in
    # 51°17'59''N
    # 51°17'59,11''N
    # 51°17,99'N
    # 51.29

    return(coord_dd)
