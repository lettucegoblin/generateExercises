import lmql
import random
import json
import datetime

# import HelperWeight.py from same directory
from HelperWeight import calculatePossibleWeightRange

outputFile = "/home/lettuce/dataGenerated.json"

# import personalDetails.json' as users array
# if file doesn't exist, initialize empty array
try:
    with open(outputFile) as json_file:
        dataGen = json.load(json_file)
        print("number of users loaded: ", len(dataGen["users"]))
except FileNotFoundError:
    dataGen = { "users": [] }

users = dataGen["users"]

#temporarily set activity to None
#for user in users:
    #user["personalData"]["activities"] = None

age = -1
weight = -1
height = -1


def calculateAge():
    global age
    age = random.randint(18, 100)
    return age


def calculateWeight(weight_class, gender):
    global age, weight, height
    # convert gender "Male" to 1
    if gender == "Male":
        g = 1
    else:
        g = 0
    # calculate possible weight range
    weightRange = calculatePossibleWeightRange(g, age, height)
    relevantRange = weightRange[weight_class]
    # pick a random weight from the range

    weight = round(random.uniform(relevantRange[0], relevantRange[1]), 2)
    return weight


def calculateHeight():
    global height
    height = random.randint(48, 96)
    return height

def randomNumberAsString(min, max):
    return str(random.randint(min, max))

@lmql.query
def exerciseLogPrompt(prompt, numberOfWorkouts=1):
    '''lmql
    sample(temperature=1.3)
        """{prompt}
        [["""
        for i in range(numberOfWorkouts):
            """{{
                "numDaysAgo": "{randomNumberAsString(0, 90)}",
                "workout": {{
                    "type": "[WORKOUT_VALUE]",
                    "wasDifficult": "[BOOLEAN_VALUE]",
                    "avgHeartRate": "[INT_VALUE]",
                    "distanceInMeters": "{randomNumberAsString(1, 16000)}",
                    "reps": "{randomNumberAsString(0, 40)}",
                    "sets": "{randomNumberAsString(1, 20)}",
                    "weightInPounds": "{randomNumberAsString(1, 250)}",
                    "durationInMinutes": "{randomNumberAsString(1, 60*3)}",
                    "location": "[STRING_VALUE]",
                    "notes": "[STRING_VALUE]",
                    "numOfComments": "{randomNumberAsString(0, 4)}",
                    "numOfLikes": "[INT_VALUE]"
                }}
            }},"""
        
    from lmql.model("TheBloke/Wizard-Vicuna-30B-Uncensored-GPTQ")
    where 
        STOPS_BEFORE(STRING_VALUE, '"') and BOOLEAN_VALUE in ["true", "false"] and INT(INT_VALUE) and len(TOKENS(INT_VALUE)) < 3 and WORKOUT_VALUE in set(["run", "bike", "walk", "cardio", "strength"])
    '''

@lmql.query
def exerciseLogComment(prompt, author):
    '''lmql
    sample(temperature=1.3)
        """{prompt}
        {{
            "author_id": {author["id"]},
            "author": "{author["personalData"]["online_handle"]}",
            "comment": "[STRING_VALUE]",
            "isLookingForReplyFromAuthor": "[BOOLEAN_VALUE]",
            "numOfLikes": "[INT_VALUE]"
        }}
        """
    from lmql.model("TheBloke/Wizard-Vicuna-30B-Uncensored-GPTQ")
    where 
        STOPS_BEFORE(STRING_VALUE, '"') and INT(INT_VALUE) and len(TOKENS(INT_VALUE)) < 2 and BOOLEAN_VALUE in ["true", "false"]
    '''

# generate random letter from a-z (randomly capitalized default)
def randomLetter(case_sensitive=False, is_capital = False):
    if case_sensitive:
        if is_capital:
            return chr(random.randint(65, 90))
        else:
            return chr(random.randint(97, 122))
    else:
        if random.randint(0, 1) == 0: # randomly capitalize
            return chr(random.randint(65, 90))
        else:
            return chr(random.randint(97, 122))

@lmql.query
def personalDetailsPrompt(prompt):
    '''lmql
    sample(temperature=1.0)
        """{prompt}
        {{
        "personalData": {{
        "firstName": "{randomLetter(True, True)}[STRING_VALUE]",
        "lastName": "{randomLetter(True, True)}[STRING_VALUE]",
        "genderIdentity": "[GENDER_VALUE]",
        "age": "{calculateAge()}",
        "height": "{calculateHeight()}",
        "weight_class": "[WEIGHT_VALUE]",
        """

        """
        "weight": "{calculateWeight(WEIGHT_VALUE, GENDER_VALUE)}",
        "online_handle": "{randomLetter()}[STRING_VALUE]",
        "aboutMe": "[STRING_VALUE]",
        "oneAdjectiveToDescribeMe": "[STRING_VALUE]",
        "emails": [
        "[STRING_VALUE]",
        "{randomLetter(True)}[STRING_VALUE]"
        ]
        }},
        "isAdmin": "[BOOLEAN_VALUE]"
        }}
        """
    from lmql.model("TheBloke/Wizard-Vicuna-30B-Uncensored-GPTQ")
    where
        STOPS_BEFORE(STRING_VALUE, '"') and GENDER_VALUE in ["Male", "Female"] and BOOLEAN_VALUE in ["true", "false"] and WEIGHT_VALUE in ["underweight", "normal", "overweight", "obese", "clinically_obese"]
    '''

def formatJson(prompt, json):
    # remove prompt
    json = json.replace(prompt, "")
    # remove \n if they're outside of strings
    json = json.replace("\n", "")

    return json

# INT(INT_VALUE) and len(TOKENS(INT_VALUE)) == 2

def generateUsers(numUsers):
    for i in range(numUsers):
        print(f"Generating user: {i} of {numUsers}")
        userJson = generateUserJson()
        users.append(json.loads(userJson))
        print(userJson)
        # every 5 users, save data
        if(i % 5 == 0):
            saveData()
    saveData()


def generateUserJson():
    prompt = "Write a summary of a random real person's personal information:"
    #prompt = "Write a summary of a random real person’s personal information, such as their name (e.g., Maria Garcia, James Smith, or Wei Zhang), email (e.g., mgarcia@gmail.com, james.smith@yahoo.com, or wei.zhang@hotmail.com):"
    outputUserJson = personalDetailsPrompt(prompt)[0].prompt
    formattedUserJson = formatJson(prompt, outputUserJson)
    return formattedUserJson

def generateExerciseLogs(users):
    generatedExerciseNumber = 0
    for user in users:
        userInfo = user.get("personalData")
        if(userInfo.get("activities") != None):
            continue # user already has exercise log
        userInfo["activities"] = generateExerciseLog(userInfo)
        generatedExerciseNumber += 1
        if(generatedExerciseNumber % 5 == 0):
            saveData()
    saveData()

def printUserInfo(userInfo):
    print(f"User: {userInfo['firstName']} {userInfo['lastName']} aka {userInfo['online_handle']}\nAge: {userInfo['age']} Height: {userInfo['height']} Weight: {userInfo['weight']}\n About me: {userInfo['aboutMe']} One adjective to describe me: {userInfo['oneAdjectiveToDescribeMe']}\n")
# generateUsers(2)
def generateExerciseLog(userInfo):
    print("Generating exercise log for user: ")
    printUserInfo(userInfo)
    # activities: [{ date: "", workout: {type:'run/bike/walk/cardio/strength', distance: 0, duration: 0, avgPace: 0, calories: 0, location: "" }}]
    prompt = f"Write an exercise log of a {userInfo['genderIdentity']} {userInfo['age']} year old who's in the {userInfo['weight_class']} weight class. They wrote this about themselves \"{userInfo['aboutMe']}\" and descibe themselves as {userInfo['oneAdjectiveToDescribeMe']}.\nExercise Log:"
    numberOfWorkouts = random.randint(1, 4)
    outputExerciseLog = exerciseLogPrompt(prompt, numberOfWorkouts)[0].prompt
    # remove trailing comma and close array with ]
    outputExerciseLog = outputExerciseLog[:-1] + "]"
    formattedExerciseLog = formatJson(prompt, outputExerciseLog)
    print(formattedExerciseLog)
    return json.loads(formattedExerciseLog)

def generateComments(currentUser, commentUsers, numComments):
    comments = []
    numComments = min(numComments, len(commentUsers)) # if there are less users than comments, use all users

    for i in range(numComments):
        author = commentUsers[i]
        
        workoutWithTwoCurlyBraces = "{" + str(currentUser["personalData"]["activities"][0]["workout"]) + "}"

        if(author["id"] == currentUser["id"]):
            # if there's other comments, use the last comment as the prompt
            if(len(comments) > 0):
                # check if any comments are looking for a reply
                # default: get last comment
                commentToReplyTo = comments[-1]

                for comment in comments:
                    if(comment["isLookingForReplyFromAuthor"] == "true"):
                        commentToReplyTo = comment
                        break

                # prompt: You've posted an exercise log. This is a comment on your exercise log. Mention something specific:
                #prompt = f"Comment: {commentToReplyTo['comment']} \n You've posted an exercise log. This is a comment on your exercise log. Respond to the comment:"
                prompt = f"You are playing the role of {currentUser['personalData']['online_handle']} who is Your personality type is {currentUser['personalData']['oneAdjectiveToDescribeMe']}. \nComment: {commentToReplyTo['author']} commented on your exercise log! They said {commentToReplyTo['comment']} \n They want a reply from you. \nRespond to the comment:"
            else:
                continue # don't comment for your own exercise log (for now)
                #prompt = f"You've posted this exercise log: {workoutWithTwoCurlyBraces} \n You've forgotten to mention something in your exercise notes. Use I and not You since you're talking about yourself:"          
        else:
            prompt = f"{currentUser['personalData']['online_handle']}'s exercise log:{workoutWithTwoCurlyBraces} \n Your personality type is {currentUser['personalData']['oneAdjectiveToDescribeMe']}. Write a comment on their exercise log. Mention something specific:"
        outputComment = exerciseLogComment(prompt, author)[0].prompt
        formattedComment = formatJson(prompt, outputComment)
        comments.append(json.loads(formattedComment))
    return comments


def getRandomUsers(users, numUsers):
    return random.sample(users, min(numUsers, len(users)))

def generateExerciseLogsComments(users):
    numberOfCommentsGenerated = 0
    tempCommentCount = 0
    for user in users:
        userInfo = user.get("personalData")
        if(userInfo.get("activities") != None):
            for activity in userInfo.get("activities"):
                numComments = int(activity.get("workout").get("numOfComments"))
                comments = activity.get("workout").get("comments")
                tempCommentCount = numberOfCommentsGenerated
                if(numComments != None and int(numComments) > 0 and comments == None):
                    # get random users to comment
                    randomUsers = getRandomUsers(users, numComments)
                    comment = generateComments(user, randomUsers, numComments)
                    activity["workout"]["comments"] = comment
                    print(f"Generated comments for user: {userInfo['online_handle']} \n {comment['author']}: {comment['comment']}")
                    numberOfCommentsGenerated += numComments
                    
                if(tempCommentCount != numberOfCommentsGenerated): # if comments were generated
                    print(f"Generated {numberOfCommentsGenerated - tempCommentCount} comments for user: {userInfo['online_handle']}")
                    saveData()

def saveData():
    with open(outputFile, "w") as outfile:
        json.dump(dataGen, outfile, indent=2)
        print("Saved data to: ", outputFile)

#generateUsers(100)
# set id for each user being their index in the array
for i in range(len(users)):
    users[i]["id"] = i
generateExerciseLogs(users)
print(users)
# generate comments for each exercise log
# Use different users to generate comments
generateExerciseLogsComments(users)

saveData()
