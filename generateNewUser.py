'''
Name:               Seow Wee Hau Winston
Name Of File:       generateNewUser.py

Input-Output Files: None - Makes Request To Server

#-----------------------------------------------------------#
This file is made for GENERATING NEW USERS. Each function in
this file is meant solely for updating .txt files to add the
user.
#-----------------------------------------------------------#
'''
import os
import msvcrt
import socket


CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
#-------------------#
# Define File Path
#-------------------#
def getFullFilePath(fileName):
  fullFilePath = os.path.join(CURRENT_DIRECTORY,"TxtFiles",fileName)
  return fullFilePath

#-------------------------------------------------#
# GENERATE all necessary information for new user #
#-------------------------------------------------#
def createNewUser(userName, userPass, connection):
  newUser_Message = ""
  while newUser_Message == "":
    # FIRST, Check If Username Already Exists. First, in "usersPendingDeletion.txt". Second, in "passwd.txt".
    isTakenUsername = False
    filePath = getFullFilePath("usersPendingDeletion.txt")
    with open(filePath, 'r') as readableFile:
      readableFileLines = readableFile.readlines()
    for eachLine in readableFileLines:
      if not("#" in eachLine):
        if userName.capitalize() == eachLine.replace("\n",""):
          newUser_Message = "<USERNAME_TAKEN>"
          isTakenUsername = True
          break
    
    filePath = getFullFilePath("passwd.txt")
    with open(filePath, 'r') as readableFile:
      readableFileLines = readableFile.readlines()
    userNum = 1
    for eachLine in readableFileLines:
      if not("#" in eachLine) and f"User {userNum}: " in eachLine:
        if userName.capitalize() == eachLine.replace(f"User {userNum}: ","").replace("\n",""):
          newUser_Message = "<USERNAME_TAKEN>"
          isTakenUsername = True
          break
        userNum += 1
    
    # SECOND, Check If Username Is Valid
    charNum = 0
    while isTakenUsername == False:
      if userName == "" or userName[charNum] == " " or userName[charNum].isnumeric() == True:
        isTakenUsername = True
        newUser_Message = "<USERNAME_TAKEN>"
        break
      charNum += 1
      if charNum == len(userName):
        break
    if isTakenUsername == False and charNum == len(userName):
      break
  userName = userName.capitalize()
  
  # If Valid Username
  if isTakenUsername == False:
    newUser_Message = "<USERNAME_VALID>"
    # FIRST, Generate New Credentials For User In "passwd.txt" File
    userNum = 1
    for eachLine in readableFileLines:
      if not("#" in eachLine) and f"User {userNum}: " in eachLine:
        userNum += 1
    
    with open(filePath, 'a') as writeablePasswdFile:
      writeablePasswdFile.write(f"User {userNum}: {userName}\n")
      writeablePasswdFile.write(f"{userPass[::-1]}\n")
    
    # SECOND, Generate New Section For User In "discounts.txt" and "subscriptions.txt" Files
    # Understand How Many Services There Are
    filePath = getFullFilePath("services.txt")
    numOfServices = 0
    with open(filePath, 'r') as readableFile:
      readableFileLines = readableFile.readlines()
    
    for eachLine in readableFileLines:
      if not("#" in eachLine) and eachLine.replace("\n","").isnumeric() == False and eachLine.replace("\n","") != "":
        numOfServices += 1
    
    # Depending On numOfServices, Add 0 To Each Discount/Subscription
    filePath = getFullFilePath("discounts.txt")
    for x in range(0,2):
      userNum = 1
      with open(filePath, 'r') as readableFile:
        readableFileLines = readableFile.readlines()
      
      for eachLine in readableFileLines:
        if not("#" in eachLine) and f"User {userNum}: " in eachLine:
          userNum += 1
      
      with open(filePath, 'a') as writeableFile:
        writeableFile.write(f"User {userNum}: {userName}\n")
        if "subscriptions.txt" in filePath:
          for i in range(0,numOfServices):
            writeableFile.write("-\n0\n")
        else:
          for i in range(0,numOfServices):
            writeableFile.write("0\n")
      filePath = getFullFilePath("subscriptions.txt")
  
  # <<Send Data To Client To Confirm Valid Username And Password>> #
  connection.send(newUser_Message.encode())
  
  return userName, userPass