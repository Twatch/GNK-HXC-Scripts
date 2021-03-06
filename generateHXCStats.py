""" A simple script to generate stats reports for the GNK-HXC challenge.

Args:
    csvFileName (str): The file system path/name of a CSV file containing data in the GNK-HXC format.  WARNING: Any
                     deviations from this are not supported!
Returns:
     str: A console output of the various stats.
"""

# TODO: Currently all stats are returned everytime, would be a nicer utility to be able to invoke the script for
#       specific stats.

import csv
import sys

import math

from fractions import Fraction

###################
# Utility Methods #
###################
def extractCSVDataToKVStore(csvFileName):
    """ Converts CSV data into a more easily usable data structure, a Key-Value Store.

    Args:
        csvFileName (str): The file system path/name of a CSV file containing data in the GNK-HXC format.  WARNING: Any
                         deviations from this are not supported!
    Returns:
        list: A Key-Value store, aka an array of dict's, each dict being key'd on the CSV's column headers and having a
               row's values.
    """
    with open(csvFileName, newline='') as csvfile:
        csvReader = csv.reader(csvfile, delimiter=',', quotechar='|')

        # An array of dictionaries, each dictionary containing each character's data from the CSV.
        kvStore = []

        # Stores each column header (ex. Character Level), to record the order they appear in the data CSV.
        # This will help us keep track of which number column each column header is.
        columnHeaderList = []

        # Loop through each row in the CSV..
        for csvRow in csvReader:
            # If the length of columnHeader list is 0, that means we haven't parsed the headers yet, therefore, do so.
            if len(columnHeaderList) < 1:
                # Place each row in our column header list, and also create a blank array in our masterData dict.  These
                # arrays will eventually contain the actual numbers/strings for each category.
                # Example: Category = 'Character Name', Value = 'Burbonrogue'
                for csvColumnHeader in csvRow:
                    columnHeaderList.append(csvColumnHeader)

            # Otherwise, we're just populating another row of character data in our KV Store.
            else:
                characterData = {}

                for index, csvCellValue in enumerate(csvRow):

                    # First, get which header's data list this value should go into, by matching the index to the header
                    # using our column header list.
                    dataKey = columnHeaderList[index]

                    # Then in our master data dict, we add the value of this CSV cell to the list of values for that
                    # column header.
                    characterData[dataKey] = csvCellValue

                kvStore.append(characterData)

    return kvStore


def groupKVStoreByColumn(columnStatsKVStore, columnToGroupBy):
    """ A utility method to group our data by the distinct values of a given data column.

    Args:
        columnStatsKVStore(list): A Key-Value store, aka an array of dict's, each dict being key'd on the CSV's column
               headers and having a row's values.
        columnToGroupBy (str): The column to group row data by

    Returns (dict): A dictionary with keys being distinction values of the 'columnToGroupBy', and values being a list of
                     character data dicts containing that distinct value.
    """
    groupedKVStore = {}
    for characterDict in columnStatsKVStore:
        # If the column value already has an entry in the grouped store, simply add this character's data to that
        # existing list
        currentColValue = characterDict[columnToGroupBy]
        if currentColValue in groupedKVStore:
            groupedKVStore[currentColValue].append(characterDict)

        # Otherwise, create an entry for the current player, with the value being a list with this one character data.
        else:
            groupedKVStore[currentColValue] = [characterDict]

    return groupedKVStore

# TODO - Allow for number formatting
def generateMonocharcterString(character, length):
    """ A utility method to generate a monocharacter string of a given length.

    Args:
        character (str): The character that should comprise the string.
        length (number): The desired length of the string.

    Returns:
        str: A monocharacter string of a given length.
    """
    monoCharString = ""
    i = 0
    while i < length:
        monoCharString = monoCharString + character
        i += 1

    return monoCharString

def printSortedDict(printDict, sectionTitle):
    """ A utility method to sort and console-print a dict.

    Args:
        printDict (dict): An arbitrary dict, with mutually sortable values.
        sectionTitle (str): Optional. A field title to print above the dict.
    """
    # Finally sort descending our dictionary of Number-of-characters-by-Player, and print.
    printDict = sorted(printDict.items(), key=lambda x: x[1], reverse=True)

    print(sectionTitle + '\n' + generateMonocharcterString('-', len(sectionTitle)))

    for printDictEntry in printDict:
        print(printDictEntry[0], ":", printDictEntry[1])

    print("\n")

##########################
# By-Player Stat methods #
##########################
def printNcByPlayer(kvStoreGroupedByPlayer):
    """ A method to print the NC (Number of Characters) stat for each player.

    Args:
        kvStoreGroupedByPlayer (dict): A dict with Keys being the Players, and values being a list of each data row for
         for that player.
    """
    numCharactersByPlayerDict = {}

    # This is simple enough, since we can just check the length of the list characters for each player.
    for player, characterList in kvStoreGroupedByPlayer.items():
        numCharactersByPlayerDict[player] = len(characterList)

    printSortedDict(numCharactersByPlayerDict, 'NC (Number of Characters)')

def printGlgByPlayer(kvStoreGroupedByPlayer):
    """ A method to print the GLG (Gross Levels Gained) stat for each player.

    Args:
        kvStoreGroupedByPlayer (dict): A dict with Keys being the Players, and values being a list of each data row for
         for that player.
    """
    glgByPlayerDict = {}

    # For each player, loop through each of their characters and total up all the levels
    # Finally store the final total in dictionary under that player's name for easy-printin' later.
    for player, characterList in kvStoreGroupedByPlayer.items():
        currentPlayerGlg = 0
        for character in characterList:
            currentPlayerGlg += int(character['Level'])

        glgByPlayerDict[player] = currentPlayerGlg

    printSortedDict(glgByPlayerDict, 'GLG (Gross Levels Gained)')

def printHlcByPlayer(kvStoreGroupedByPlayer):
    """ A method to print the HLC (Highest Character Level) stat for each player.

    Args:
        kvStoreGroupedByPlayer (dict): A dict with Keys being the Players, and values being a list of each data row for
         for that player.
    """
    hlcByPlayerDict = {}

    # For each player, loop through each of their characters comparing each to find the max.
    # Finally store the final winner in dictionary under that player's name for easy-printin' later.
    for player, characterList in kvStoreGroupedByPlayer.items():
        currentPlayerHighestLevel = 0
        for character in characterList:
            currentPlayerHighestLevel = max(currentPlayerHighestLevel, int(character['Level']))

        hlcByPlayerDict[player] = currentPlayerHighestLevel

    printSortedDict(hlcByPlayerDict, 'HCL (Highest Character Level)')

def printAclByPlayer(kvStoreGroupedByPlayer):
    """ A method to print the ACL (Average Character Life) stat for each player.

    Args:
        kvStoreGroupedByPlayer (dict): A dict with Keys being the Players, and values being a list of each data row for
         for that player.
    """
    aclByPlayerDict = {}

    # For each player, loop through each of their characters and total up all the levels, then divided by number of
    # characters to calculate Average Character Life.
    # Finally store the final total in dictionary under that player's name for easy-printin' later.
    for player, characterList in kvStoreGroupedByPlayer.items():
        totalCharacterLevels = 0
        for character in characterList:
            totalCharacterLevels += int(character['Level'])

        # Compute ACL by dividing total levels by number of characters, and finally round down any decimals.
        aclByPlayerDict[player] = math.floor(totalCharacterLevels / len(characterList))

    printSortedDict(aclByPlayerDict, 'ACL (Average Character Life)')

def printMdlByPlayer(kvStoreGroupedByPlayer):
    """ A method to print the MDL (Mean Death Level) stat for each player.

    Args:
        kvStoreGroupedByPlayer (dict): A dict with Keys being the Players, and values being a list of each data row for
         for that player.
    """
    mdlByPlayerDict = {}

    # For each player, loop through each of their characters and total up all the levels of dead characters then
    # divide by the number of dead characters, unless a character has no dead characters.
    # Finally store the final total in dictionary under that player's name for easy-printin' later.
    for player, characterList in kvStoreGroupedByPlayer.items():
        totalDeadCharacterLevels = 0
        numberOfDeadCharacters = 0
        for character in characterList:
            if character['Cause of Death']:
                totalDeadCharacterLevels += int(character['Level'])
                numberOfDeadCharacters += 1

        # Compute MDL by dividing total levels of dead charactes by number of dead characters, and then rounding down.
        # If there are no dead characters, just set to 0 to avoid trying to divide by 0.
        if numberOfDeadCharacters > 0:
            mdlByPlayerDict[player] = math.floor(totalDeadCharacterLevels / numberOfDeadCharacters)
        else:
            mdlByPlayerDict[player] = 0

    printSortedDict(mdlByPlayerDict, 'MDL (Mean Death Level)')

def printByPlayerStats(columnStatsKVStore):
    """ A method to print various stats that attributed to individual players.

    Args:
        columnStatsKVStore (list): A list of dicts, each dict being key'd on the data CSV's column headers and having a
               row's values.
    """
    kvStoreGroupedByPlayer = groupKVStoreByColumn(columnStatsKVStore, 'Character Player')

    # Print each of the stats using our By-Player KV store
    printNcByPlayer(kvStoreGroupedByPlayer)
    printGlgByPlayer(kvStoreGroupedByPlayer)
    printHlcByPlayer(kvStoreGroupedByPlayer)
    printAclByPlayer(kvStoreGroupedByPlayer)
    printMdlByPlayer(kvStoreGroupedByPlayer)

######################
# Death Stat methods #
######################
def printDeathStats(columnStatsKVStore):
    """ A method to print various stats that describe global aspects of character death.

    Args:
        columnStatsKVStore (list): A list of dicts, each dict being key'd on the data CSV's column headers and having a
               row's values.
    """
    # Grab our 'Cause of Death' off each Character Entry
    killedByMobList = []
    for characterDict in columnStatsKVStore:
        killedByMobList.append(characterDict['Cause of Death'])

    # Create a set of the killed by mobs (Set = List, but with no duplicate entries).
    killedByMobSet = set(killedByMobList)
    killedByMobDict = {}
    totalDeaths = 0
    totalAlive = 0

    # For each unique mob, get the number of occurances of that mob in the list, aka it's total kill count
    # That count will be placed in a new dict, for easy sorting and printing.
    for mob in killedByMobSet:
        # ASSUMPTION - A blank value here means the character is still alive, thus not relevant for this stat, and will
        #              will be skipped.
        if mob != '':
            killedByMobDict[mob] = killedByMobList.count(mob)
            totalDeaths += killedByMobDict[mob]
        else:
            totalAlive = killedByMobList.count(mob)

    printSortedDict(killedByMobDict, 'Cause of Death (' + str(totalDeaths) + ')')

    # Next Print the Dead-to-Living ratio
    deadToLivingFracation = Fraction(totalDeaths, totalAlive)

    print("\nDead-to-Living Ratio: " + str(deadToLivingFracation))

    print("\n")

#########################
# By-Class Stat methods #
#########################
def printByClassStats(columnStatsKVStore):
    """ A method to print various stats that attributed to each Class.

    Args:
        columnStatsKVStore (list): A list of dicts, each dict being key'd on the data CSV's column headers and having a
               row's values.
    """
    # Group our KV Store by Class
    kvStoreGroupedByClass = groupKVStoreByColumn(columnStatsKVStore, 'Class')

    # Calculate and print Survival % by class.
    survivalPercentByClassDict = {}

    # This is simple enough, since we can just check the length of the list characters for each player.
    # Need to spell class MK-style, because 'class' is a reserved word in Python.
    for klass, characterList in kvStoreGroupedByClass.items():
        livingCharacters = 0

        for character in characterList:
            if not character['Cause of Death']:
                livingCharacters += 1

        # Calculate survival rate by dividing living characters by total characters.
        survivalPercentage = livingCharacters / len(characterList)
        survivalPercentByClassDict[klass] = survivalPercentage

    # Finally sort descending our dictionary of Surivial-Rate-by-Class, and print.
    survivalPercentByClassDict = sorted(survivalPercentByClassDict.items(), key=lambda x: x[1], reverse=True)

    print("Survival Rate By Class\n--------")

    # Print each survival percentage, formatted to appear as a percentage rather than a plain decimal.
    for classSurvivalRate in survivalPercentByClassDict:
        print(classSurvivalRate[0], ":", "%i" % (classSurvivalRate[1] * 100), "%")

    print("\n")

if len(sys.argv) < 2:
    print("Must specify .csv file to generate queries from.")
    exit(-1)
else:
    # The column dictionary with all our CSV Data by column.  Data organized like this will be best for grabbing global
    # stats related to just one stat like "Deadliest Mob".
    characterDataKVStore = extractCSVDataToKVStore(sys.argv[1])

    printByPlayerStats(characterDataKVStore)

    printDeathStats(characterDataKVStore)

    printByClassStats(characterDataKVStore)