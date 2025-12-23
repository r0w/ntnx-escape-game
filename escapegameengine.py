import time
import sys
import json
from jsonpath_ng.ext import parse
import cursor
from CheckLabs import *
import random
from Sentences import *
from actions import *
from main import labAnswersJsonFile,forceSilentModeDuringChecks
import os
import re

# ========================================================================
# = deleteEnptyStrings
# ========================================================================
# This function clean a list from empty strings
def deleteEnptyStrings(tab):
    return [s for s in tab if s != ""]

# ========================================================================
# = display
# ========================================================================
# This function displays a string letter by letter with a delay, handling colors and specific behaviors
# if the string contains :
#  - #>P:x#, where x is a number, the function will pause for x seconds.
#  - #>I:<name>#, it will wait for a user input and store it in the dictionary variables.
#  - #>V:<name>#, it will display the value of the variable <name> in the dictionary variables.
#  - #>A:<name>#, it will execute an action. The name of the action is the name of the function to call.
#  - #>S# will display the Sharp (#) character.
#  - #>C:<color>#, it will change the color of the text to <color>.
#  - #>D#, it will switch back to the default color.
#  - #>B#, it will clear the screen.
#  - #>N#, no prompt (only works at the beginning of a line).

  
def display(prompt, inputStrings, variables, color = None, waitForInputValue = '', delay=0.03):
    # Setting up colors.
    # https://www.geeksforgeeks.org/python/print-colors-python-terminal/
    color_codes = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m'
    }

    if variables['Debug']==True:
        # We remove delay
        delay = 0

    cursor.show()
      
    # Set default color if specified.
    if color and (color in color_codes):
        sys.stdout.write(color_codes[color])
    
    # Input strings are available?
    if inputStrings and len(inputStrings) > 0 :

        # We browse the input strings one by one
        for inputString in inputStrings:

            # First we split the strings by the # character
            inputElements = deleteEnptyStrings(inputString.split("#"))

            # Has prompt to be printed before displaying any other element?
            if (len(inputElements) > 0) and (len(prompt) > 0) :
                if inputElements[0] != ">N" :
                    sys.stdout.write("<" + prompt + "> ")
                    sys.stdout.flush()

            # Then we iterate over the elements of the list
            for element in inputElements:

                # We check if we have a spcial action to do.
                if len(element) > 0 and element[0] == '>' :
                    # If we have a pause action, we wait for the specified number of seconds.
                    if element[1]=='P' and variables['Debug']==False:
                        cursor.hide()

                        for _ in range(int(element[3:])):  # Blink 5 times
                            sys.stdout.write('_')
                            sys.stdout.flush()
                            time.sleep(0.5)
                            sys.stdout.write('\b \b')
                            sys.stdout.flush()
                            time.sleep(0.5)

                        cursor.show()

                    # If we have a color change action, we change the color of the text.
                    elif element[1] == 'C':
                        newColor = element[3:]
                        if newColor and (newColor in color_codes):
                            sys.stdout.write(color_codes[newColor])

                    # If we have a default color action, we switch back to the default color.
                    elif element[1] == 'D':
                        if color and (color in color_codes):
                            sys.stdout.write(color_codes[color])

                    # If we have a clear screen action, we clear the screen.
                    elif element[1] == 'B':
                        os.system('cls' if os.name == 'nt' else 'clear')

                    # If we have an action, we call the function with the name specified in the string.
                    elif element[1] == 'A':
                        globals()[element[3:]](variables)

                    # If we have a read action, we wait for the user to press enter and store the input in the variables dictionary.
                    elif element[1] == 'I':
                        if len(element) > 3:
                            # Loop until we have a good value.
                            stayInLoop = True
                            while stayInLoop:
                                try:
                                    # Get value.
                                    sys.stdout.write(color_codes['yellow'])
                                    value = input()
                                    
                                    if value:
                                        variables[element[3:]] = value
                                        stayInLoop = False
                                    else: 
                                        display("", ["Please enter a value..."], variables, color, waitForInputValue)
                                        
                                except EOFError:
                                    print("")
                            
                            sys.stdout.write(color_codes[color])
                        else:
                            # Just wait for an input.
                            sys.stdout.write(color_codes['yellow'])
                            readInput = input()
                            sys.stdout.write(color_codes[color])
                            if readInput.lower() != waitForInputValue.lower() and waitForInputValue != '':
                                display(prompt, [labNotUnderstood[variables['Language']]], variables, "red", waitForInputValue)
                        
                    # If we have a variable display action, we display the value of the variable specified in the string
                    elif element[1] == 'V':
                        display("", [variables[element[3:]]], variables)

                    # Display the Sharp (#) character.
                    elif element[1] == 'S':
                        sys.stdout.write("#")
                else:
                    # If no special action, we display the string letter by letter.
                    for letter in element:
                        sys.stdout.write(letter)
                        sys.stdout.flush()
                        time.sleep(delay)   
    


# ========================================================================
# = stageMessage
# ========================================================================
# This function reads a JSON file and returns the message of a specific stage

def stageMessage(id_number, json_file_path, language='en'):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    info = parse('$.stages[?(@.id=' + str(id_number) + ')]').find(data)[0].value

    if 'WaitForInputValue' in info:
        waitForInputValue = info['WaitForInputValue']
    else:
        waitForInputValue = ''

    if 'CheckTask' in info:
        checkTask = info['CheckTask']
    else:
        checkTask = ''
 
    if language not in info['Messages'].keys():
        language = 'en'
 
    return(info['Prompt'] if 'Prompt' in info else "-:-", info['Messages'][language], info['DefaultColor'], waitForInputValue, checkTask, info['SaveScore'] if 'SaveScore' in info else True)


# ========================================================================
# = clueMessage
# ========================================================================
# This function reads a JSON file and returns the message of a specific check function
def clueMessage(checkScript, messageNumber, language='en'):
    with open(labAnswersJsonFile, 'r') as file:
        data = json.load(file)
  
    jsonpath_expr=parse('$.answers[?(@.checkFunction=="'+checkScript+'")].clues')
    
    info = jsonpath_expr.find(data)[0].value   
    
    if language not in info[messageNumber].keys():
        language='en'
     
 
    return(info[messageNumber][language])


# ========================================================================
# = CheckStage
# ========================================================================
# This function checks the script of a stage to validate stage completion
def CheckStage(checkScript, prompt, color, variables, silent = False):
    if checkScript in globals():
        ret = False
        
        # We do force silent mode for predefinied checks.
        if checkScript in forceSilentModeDuringChecks:
            silent = True
        
        while not ret:
            ret, messageNumber, reenterValue = globals()[checkScript](variables, recoveryMode = silent)
                
            if silent:
                errorMessage = ""
                retryMessage = ""

            else:
                errorMessage = random.choice(labKo[variables['Language']]) + "\n"

                if reenterValue != None:
                    retryMessage = labRetryWithValue[variables['Language']]
                else:
                    retryMessage = labRetry[variables['Language']]
        
            
            # If function returns unsuccessful message
            if not ret:
                
                clue = clueMessage(checkScript, messageNumber, variables['Language'])
                
                if silent :
                        display(prompt, ["#>P:3#" + clue], variables, color) 

                else:
                    if reenterValue != None:
                        display(prompt, [ "#>C:red#" + errorMessage + "#>D##>P:3#\n"], variables, color) 
                        display(prompt, [ clue], variables, color) 
                        display(prompt, [ retryMessage + "#>I:" + reenterValue], variables, color) 
                    else:
                        display(prompt, [ "#>C:red#" + errorMessage + "#>D##>P:3#\n"], variables, color) 
                        display(prompt, [ clue], variables, color) 
                        display(prompt, [ retryMessage + "#>I:"], variables, color) 
            else:
                # If function returns successful message
                if silent == False:
                    display(prompt, [random.choice(labOk[variables['Language']]) + "#>P:3#\n\n"], variables, color)
    else:
        raise ValueError(f"Function {checkScript} is not defined.")
    

# ========================================================================
# = GetSupportedLanguages
# ========================================================================
# This function reads a JSON file and returns the list of supported languages
def GetSupportedLanguages(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    return ",".join(data['supportedLanguages'])


# ========================================================================
# = UpdateScoreFile
# ========================================================================
# This function updates the score file with the format Trigram:Stage
def UpdateScoreFile(scoreFolder, trigram, stage, maxStage, variables=None):
    
    # We setup the score filename for this user
    scoreFile=scoreFolder + "/" + trigram + ".json"
    
    # Load the existing scores from the JSON file
    try:
        # Try to open the score file and read the content
        with open(scoreFile, 'r' ) as file:
            scoreJson = json.load(file)
            scoreJson['value'] = stage  # Update the stage value
            scoreJson['lastUpdated'] = time.strftime("%H:%M:%S", time.localtime())
    except:
        # If file does not exist, create a new score structure
        scoreJson = {'value': stage, 'startTime': time.strftime("%H:%M:%S", time.localtime()), 'lastUpdated':time.strftime("%H:%M:%S", time.localtime()), 'finishedTime': "",'duration':""}

    # # Update the score for the given trigram
    # jsonpath_expr = parse('$.score[?(@.player == "' + trigram + '")]')
    # result = jsonpath_expr.find(score)

    # Save the username if available
    if variables and "Username" in variables and variables["Username"]:
        username = str(variables["Username"]).strip()
        if username and "username" not in scoreJson:
            scoreJson["username"] = username

    # Check is the game is finished
    if stage >= maxStage:
        scoreJson['finishedTime'] = time.strftime("%H:%M:%S", time.localtime())
        # Calculate duration in seconds and format as HH:MM:SS
        start_struct = time.strptime(scoreJson['startTime'], "%H:%M:%S")
        finish_struct = time.strptime(scoreJson['finishedTime'], "%H:%M:%S")
        start_seconds = start_struct.tm_hour * 3600 + start_struct.tm_min * 60 + start_struct.tm_sec
        finish_seconds = finish_struct.tm_hour * 3600 + finish_struct.tm_min * 60 + finish_struct.tm_sec
        duration_seconds = max(0, finish_seconds - start_seconds)
        hours = duration_seconds // 3600
        minutes = (duration_seconds % 3600) // 60
        seconds = duration_seconds % 60
        scoreJson['duration'] = f"{hours:02}:{minutes:02}:{seconds:02}"
        

    # Write the updated score back to the JSON file
    try:
        with open(scoreFile, 'w') as file:
            json.dump(scoreJson, file, indent=4)
    except FileNotFoundError:
        print("Error, unable to write to the score file. Please check the path and permissions.")
        sys.exit(4)


# ========================================================================
# = gameClean
# ========================================================================
# This function clean the scoreboard file
def gameClean(scoreFolder,maxStages):
    
    # We check if the score folder exists, if not we create it
    if not os.path.exists(scoreFolder):
        os.makedirs(scoreFolder)
    
    # We create the maxStage file
    score={
        'maximumScore': maxStages
    }

    # Write the maxStage file
    with open(scoreFolder + "/maxStage.json", 'w') as file:
        json.dump(score, file, indent=4)

    # We remove all files in the score folder that match the pattern [A-Za-z0-9]{3}\.json
    for filename in os.listdir(scoreFolder):
        if re.fullmatch(r'[A-Za-z0-9]{3}\.json', filename):
            try:
                os.remove(os.path.join(scoreFolder, filename))
            except Exception as e:
                print(f"Error removing {filename}: {e}")
