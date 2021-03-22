'''
Name:               Seow Wee Hau Winston
Name Of File:       generalServer.py

Input-Output Files: discounts.txt, invoices.txt, orderInCart.txt,
                    passwd.txt, services.txt, subscriptions.txt,
                    usersForgotPassword.txt, usersPendingDeletion.txt,
                    winstonBusinessInfo.txt

#-----------------------------------------------------------#
This file is made for SERVER FOR BOTH admins and clients.
This server will determine the request made from either
user and will determine the appropriate response.
#-----------------------------------------------------------#
'''
import socket
import threading
import os
import generateNewUser
import userCreation
import pickle
import time
from datetime import date
import datetime
from _thread import start_new_thread


CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

#-------------------#
# Define File Path
#-------------------#
def getFilePath(fileName):
  fullFilePath = os.path.join(CURRENT_DIRECTORY,"TxtFiles",fileName)
  return fullFilePath


##########################################################################
#                                                                        #
#                                 USER OPTIONS                           #
#                                                                        #
##########################################################################
#---------------------#
# 1. Chooses Category #
#---------------------#
def server_CategoryOption(connection, buf):
  print("Received Category Choice")
  print("Processing...")
  registeredUser = None
  # If Category Option 1: Registered User
  if buf[0] == "1":
    userCredentialsArr = buf.split(",")
    userName = userCredentialsArr[1]
    userPass = userCredentialsArr[2]
    resetPassword = userCredentialsArr[3]
    
    print("Category Option 1: Registered User...")
    isValidUser = False
    checkUser_Message, listOfServices, registeredUser = checkUser(userName, userPass, resetPassword, connection, isValidUser)
    if checkUser_Message == "":
      connection.sendall("<VALIDATED_CREDENTIALS>".encode())
    # Valid Credentials
    if len(listOfServices) != 0:
      print("Valid Credentials Sent By Client.")
    else:
      print("Invalid Credentials Sent By Client.")
  # If Category Option 2: New User
  else:
    userCredentialsArr = buf.split(",")
    userName = userCredentialsArr[1]
    userPass = userCredentialsArr[2]
    
    print("Category Option 2: New User")
    resetPassword = ""
    isValidUser = True
    userName, userPass = generateNewUser.createNewUser(userName, userPass, connection)
    checkUser_Message, listOfServices, registeredUser = checkUser(userName, userPass, resetPassword, connection, isValidUser)
    if checkUser_Message == "":
      connection.sendall("<VALIDATED_CREDENTIALS>".encode())
  
  if registeredUser != None:
    time.sleep(2)
    registeredUserString = pickle.dumps(registeredUser)
    connection.send(registeredUserString)
  
  return listOfServices


#------------------------------------------------#
# Checks IF Valid User Before Grabbing User Info #
#------------------------------------------------#
def checkUser(userName, userPass, resetPassword, connection, isValidUser, listOfServices = [], registeredUser = None):
  checkUser_Message = ""
  # Validate Credentials
  if isValidUser == False and resetPassword == "":
    # Accessing File
    filePath = getFilePath("passwd.txt")
    with open(filePath, 'r') as userAccount:
      userAccountLine = userAccount.readlines()
    
    userNo = 1
    for num,value in enumerate(userAccountLine):
      if not("#" in value) and "User" in value and userName != "Admin" and userName != "User":
        # Validate Username
        if userName == value.replace(f"User {userNo}: ", "").replace("\n",""):
          encryptedPassword = userAccountLine[num+1].replace("\n","")
          # Validate Password
          if userPass == encryptedPassword[::-1]:
            isValidUser = True
            break
        userNo += 1
  
  # Request For Reset Password
  if resetPassword != "":
    hasRequestedPassReset = False
    # Determine Input
    if resetPassword == "Y":
      filePath = getFilePath("usersForgotPassword.txt")
      
      # FIRST, Check IF Requested Password Reset Before
      with open(filePath, 'r') as readableFile:
        readableFileLines = readableFile.readlines()
      
      for eachLine in readableFileLines:
        if not("#" in eachLine) and userName == eachLine.replace("\n",""):
          checkUser_Message = f"<PASSWORD_ALREADYRESET>"
          hasRequestedPassReset = True
          break
      # SECOND, Append Name To "usersForgotPassword.txt" File
      if hasRequestedPassReset == False:
        with open(filePath, 'a') as writableFile:
          writableFile.write(f"{userName}\n")
        checkUser_Message = f"<PASSWORD_RESET------->"
    else:
      checkUser_Message = f"<PASSWORD_DENYRESET--->"
    # <<Send Message To Client>>
    connection.sendall(checkUser_Message.encode())
  
  # Is Validated User
  if isValidUser:
    # GET List of Services If Not Obtained Before
    if listOfServices == []:
      filePath = getFilePath("services.txt")
      with open(filePath, 'r') as serviceAccount:
        serviceAccountLine = serviceAccount.readlines()
        for line in serviceAccountLine:
          # ADD Service And Their Cost To List of Services
          if not("#" in line):
            listOfServices.append(line.replace('\n',''))
    
    # Start Up User
    registeredUser = userCreation.User(userName, listOfServices)
    # GET Discounts
    filePath = getFilePath("discounts.txt")
    registeredUser.getDiscountsOrSub(filePath)
    
    # GET Current Subscriptions
    filePath = getFilePath("subscriptions.txt")
    registeredUser.getDiscountsOrSub(filePath)
  elif resetPassword == "":
    checkUser_Message = "<INVALID_NAMEORPASS--->"
    connection.sendall(checkUser_Message.encode())
  
  return checkUser_Message, listOfServices, registeredUser


#=============================================#
# 2. Main Menu: Search For Service [Option 1] #
#=============================================#
def server_SearchService(nameOfServiceToSearch, listOfServices, connection):
  if len(nameOfServiceToSearch) > 0:
    print("Main Menu Option 1 Selected: Search For Service")
    time.sleep(1)
    
    availableServices = []
    stringToSendClient = ""
    
    # Find Relevant Services
    if nameOfServiceToSearch != "<DISPLAYALLSERVICES>":
      for num,service in enumerate(listOfServices):
        # IF userInput is EMPTY, add all services in "services.txt"
        if num % 2 == 0:
          if nameOfServiceToSearch in service:
            availableServices.append(service.title())
    # Display All Services
    else:
      for service in range(0,len(listOfServices),2):
        availableServices.append(listOfServices[service].title())
    
    # <<Sends All availableServices To Client>>
    if len(availableServices) != 0: # Service(s) Found
      for eachItem in availableServices:
        stringToSendClient += eachItem + ","
      stringToSendClient = stringToSendClient[:-1]
    else: # No Services Found
      stringToSendClient = "<NOAVAILABLESERVICES>"
    connection.sendall(stringToSendClient.encode())   
  else:
    print("Connection has dropped.")

#**********************************************************************#
# 4. Suboption Menu 2: Retrieve Order From Previous Session [Option 2] #
#**********************************************************************#
def server_RetrievePreviousOrder(buf, con):
  print("SubOption Selection 2 Option 2 Selected: Retrieve Previous Order")
  buf = buf.split(",")
  cartOrderNo = buf[0]
  userName = buf[1]
  # Define File Path and Order Info Array
  filePath = getFilePath("orderInCart.txt")
  orderInfoArr = []
  newCartArr = []
  finishCollection = False
  stringToSendClient = ""
  # Open File
  with open(filePath, 'r') as readableFile:
    readableFile = readableFile.readlines()
  
  for eachLine in readableFile:
    # GET All Info From Orders
    if not("#" in eachLine):
      orderInfoArr.append(eachLine.replace("\n",""))
  
  # Check IF Order Requested By User Exists
  for num,eachLine in enumerate(orderInfoArr):
    # Validate Order Number
    if f"Order No: {cartOrderNo}" == eachLine:
      # Valid UserName
      if userName.title() == orderInfoArr[num+1]:
        # Links to First Service and Resets Current Cart
        startValue = num + 2         
        while True:
          nameOfService = orderInfoArr[startValue].title()
          quantityOfService = int(orderInfoArr[startValue+1])
          while quantityOfService != 0:
            newCartArr.append(nameOfService)
            quantityOfService -= 1
          startValue += 2
          if startValue >= len(orderInfoArr) or "Order No: " in orderInfoArr[startValue]:
            finishCollection = True
            break
        # Remove Cart Order From 'orderInCart.txt' File
        for eachNum, eachLine in enumerate(readableFile):
          if f"Order No: {cartOrderNo}" in eachLine:
            readableFile.pop(eachNum)
            while eachNum < len(readableFile) and not("Order No: ") in readableFile[eachNum]:
              readableFile.pop(eachNum)
            break
        with open(filePath, 'w') as writeableFile:
          writeableFile.writelines(readableFile)
  # Check If Order Is Found
  if finishCollection:
    print(f"Order {cartOrderNo} Collected For User {userName}.")
    for eachItem in newCartArr:
      stringToSendClient += f"{eachItem},"
    stringToSendClient = stringToSendClient[:-1]
  else:
    print(f"Order {cartOrderNo} Is Not Found.")
    stringToSendClient = "<NOORDER>"
  con.send(stringToSendClient.encode())


#-------------------------------------------------------#
# 5. Gets Business Info, Invoice No To Generate Invoice #
#-------------------------------------------------------#
def server_GenerateInvoiceInfo(con):
  print("Main Menu Option 3 Selected: Grab Businesss Information")
  # GET Business Info
  mybusinessInfo = []
  stringToSendClient = ""
  filePath = getFilePath("winstonBusinessInfo.txt")
  with open(filePath, "r") as readableFile:
    readableFileLines = readableFile.readlines()
    
  for eachLine in readableFileLines:
    if not("#" in eachLine):
      mybusinessInfo.append(eachLine.replace("\n",""))
  
  for eachLine in mybusinessInfo:
    stringToSendClient += eachLine + ","
  
  # GET Invoice Number
  filePath = getFilePath("invoices.txt")
  with open(filePath, 'r') as readableFile:
    readableFileLines = readableFile.readlines()
  
  ordersNumArr = []
  for eachLine in readableFileLines:
    # IF Invoice Number, Add
    if not("#" in eachLine) and "Invoice No: " in eachLine:
        ordersNumArr.append(eachLine.replace("Invoice No: ","").replace("\n",""))
  lastInvoiceNum = int(ordersNumArr[-1].replace("I",""))
  newInvoiceNum = f"I{lastInvoiceNum+1}"
  stringToSendClient += newInvoiceNum
  con.send(stringToSendClient.encode())


#==========================================#
# 6. Main Menu: Confirm Payment [Option 3] #
#==========================================#
def server_MakePayment(listOfServices, con):
  print("Main Menu Option 3 Selected: Make Payment")
  # Get The User Object + ExpirationDateArr
  registeredUser = pickle.loads(con.recv(4096))
  print("User Object Retrieved.")
  time.sleep(1)
  
  # Get Current Date
  currentDate = date.today().strftime("%Y-%m-%d")
  
  # Write Invoice To "invoices.txt"
  filePath = getFilePath("invoices.txt")
  with open(filePath, "a") as readableFile:
    readableFile.write(f"Invoice No: {registeredUser.orderNo}\n")
    readableFile.write(f"{registeredUser.userName}\n")
    readableFile.write(f"{currentDate}\n")
    for eachSer in registeredUser.myCartDict:
      readableFile.write(f"{eachSer}\n")
      readableFile.write(f"{registeredUser.myCartDict[eachSer]}\n")
  
  # Write To Update Total Subscriptions in "subscriptions.txt"
  filePath = getFilePath("subscriptions.txt")
  with open(filePath, "r") as readableFile:
    readableFileLines = readableFile.readlines()
  userNum = 1
  for num,eachLine in enumerate(readableFileLines):
    # IF Line Contains Username
    if not("#" in eachLine) and "User" in eachLine:
      if f"User {userNum}: {registeredUser.userName.title()}\n" in eachLine:
        startValue = num + 1
        for eachSer in list(registeredUser.updatedExpirationDates.keys()):
          readableFileLines[startValue] = f"{registeredUser.updatedExpirationDates[eachSer]}\n"
          readableFileLines[startValue+1] = f"{registeredUser.subscriptions[eachSer]}\n"
          startValue += 2
      userNum += 1
  
  with open(filePath, "w") as readableFile:
    readableFile.writelines(readableFileLines)
  
  # Remove Order From Cart IF It Was A Previous Order From The Cart
  if registeredUser.cartOrderNo != '':
    filePath = getFilePath("orderInCart.txt")
    with open(filePath, 'r') as readableFile:
      readableFileLines = readableFile.readlines()
    # For eachLine
    for lineNum,eachLine in enumerate(readableFileLines):
      # Remove All Contents Of The Order From The Cart
      if registeredUser.cartOrderNo in eachLine:
        readableFileLines.pop(lineNum)
        while lineNum < len(readableFileLines) and not("Order No:" in readableFileLines[lineNum]):
          readableFileLines.pop(lineNum)
    
    with open(filePath, "w") as readableFile:
      readableFile.writelines(readableFileLines)


#==========================================#
# 7. Main Menu: Change Password [Option 5] #
#==========================================#
def server_ChangePassword(buf,con):
  print("Main Menu Option 5 Selected: Change User Password")
  buf = buf.split(",")
  newPassword = buf[0]
  userName = buf[1]
  # Change Password In File
  filePath = getFilePath("passwd.txt")
  with open(filePath, 'r') as readableFile:
    readableFileLines = readableFile.readlines()
  
  userNum = 1
  for lineNum,eachLine in enumerate(readableFileLines):
    if not("#" in eachLine) and "User" in eachLine:
      if userName == eachLine.replace(f"User {userNum}: ","").replace("\n",""):
        readableFileLines[lineNum+1] = f"{newPassword[::-1]}\n"
      userNum += 1
  with open(filePath, 'w') as writableFile:
    writableFile.writelines(readableFileLines)
  con.send("Password Changed!\n".encode())


#=========================================#
# 8. Main Menu: Delete Account [Option 6] #
#=========================================#
def server_PendingDeleteAccount(userName, con):
  print("Main Menu Option 6 Selected: Delete Account")
  filePath = getFilePath("usersPendingDeletion.txt")
    
  # Add Name To The "usersPendingDeletion.txt" File
  with open(filePath,'a') as writeableFile:
    writeableFile.write(f"{userName}\n")
  
  # Remove Username and Password From The "passwd.txt" File
  filePath = getFilePath("passwd.txt")
  with open(filePath, 'r') as readableFile:
    readableFileLines = readableFile.readlines()
  
  userNum = 1
  for lineWithUser,eachLine in enumerate(readableFileLines):
    if not("#" in eachLine) and "User" in eachLine:
      if f"User {userNum}: {userName}" in eachLine: 
        readableFileLines.pop(lineWithUser) # Pops Username and Password
        readableFileLines.pop(lineWithUser) 
        with open(filePath, 'w') as writableFile:
          writableFile.writelines(readableFileLines)
        break
      userNum += 1
  con.send("<DELETED_ACCOUNT>".encode())


#===================================================#
# 9. Main Menu: Leave ESP + Save To Cart [Option 7] #
#===================================================#
def server_leavingESP(con):
  print("Main Menu Option 7 Selected: Leaving ESP")
  registeredUser = pickle.loads(con.recv(4096))
  # GET Latest Order Number
  filePath = getFilePath("orderInCart.txt")
  orderNosArr = []
  with open(filePath, 'r') as readableFile:
    readableFileLines = readableFile.readlines()
    
    for eachLine in readableFileLines:
      if "Order No:" in eachLine and not("#" in eachLine):
        orderNosArr.append(eachLine.replace("Order No: ","").replace("A","").replace("\n",""))
  
  # Enter New Cart Order Number
  newCartOrder = f"A{int(orderNosArr[-1])+1}"
  
  # Write To Cart File To Save
  with open(filePath, 'a') as readableFile:
    readableFile.write(f"Order No: {newCartOrder}\n")
    readableFile.write(f"{registeredUser.userName}\n")
    for eachSer in registeredUser.myCartDict:
      readableFile.write(f"{eachSer}\n")
      readableFile.write(f"{registeredUser.myCartDict[eachSer]}\n")
  con.send(newCartOrder.encode())



###########################################################################
#                                                                         #
#                                 ADMIN OPTIONS                           #
#                                                                         #
###########################################################################
#-------------------------------#
# 1. Validate Admin Credentials #
#-------------------------------#
def serverADMIN_checkAdmin(buf,con):
  buf = buf.split(",")
  userName = buf[0]
  userPass = buf[1]
  # Open "passwd.txt" File To GET Username And Password
  filePath = getFilePath("passwd.txt")
  with open(filePath, 'r') as readableFile:
    readableFileLines = readableFile.readlines()
    
  for num, eachLine in enumerate(readableFileLines):
    if not("#" in eachLine) and "User 1: " in eachLine:
      adminUsername = readableFileLines[num].replace("User 1: ","").replace("\n","")
      adminPassword = readableFileLines[num+1].replace("\n","")[::-1]
      break
  
  # VALIDATE Username & Password
  if userName == adminUsername and userPass == adminPassword:
    stringToSendClient = "<VALIDATED_ADMIN>"
  # IF INVALID, Request Username & Password Again
  else:
    stringToSendClient = "<INVALID_CREDENTIALS>"
  con.send(stringToSendClient.encode())
  print("Recevied Admin Credentails\nProcessing...")


#----------------------------------------#
# 2. Get Users That Are Pending Deletion #
#----------------------------------------#
def serverADMIN_getUsersPendingDeletion(con):
  nameOfUsersToDel = []
  
  # List Users Which Are Pending Deletion At "usersPendingDeletion.txt" File
  filePath = getFilePath("usersPendingDeletion.txt")
  with open(filePath, 'r') as readableFile:
    readableFileLines = readableFile.readlines()
  for user in readableFileLines:
    if not("#" in user):
      nameOfUsersToDel.append(user.replace('\n',''))
  
  # Checks Number Of Users Pending Deletion
  if len(nameOfUsersToDel) != 0:
    stringToSendClient = ""
    for eachName in nameOfUsersToDel:
      stringToSendClient += eachName + ","
    stringToSendClient = stringToSendClient[:-1]
    stringToSendClient = "<HAVE_USERS>" + stringToSendClient
  else:
    stringToSendClient = "<NO_USERS-->"
  con.send(stringToSendClient.encode())
  print("Grabbing List Of Pending Deletions")


#---------------------------------------------#
# 3. Suboption Menu 1: Delete User [Option 1] #
#---------------------------------------------#
def serverADMIN_deleteUser(userName, con):
  ## FIRST, Remove User From "usersPendingDeletion.txt" File
  filePath = getFilePath("usersPendingDeletion.txt")
  with open(filePath, 'r') as readableFile:
    readableFileLines = readableFile.readlines()
  
  for lineNum,nameOfUser in enumerate(readableFileLines):
    if userName == nameOfUser.replace("\n", ""):
      readableFileLines.pop(lineNum)
    with open(filePath, 'w') as writableFile:
      writableFile.writelines(readableFileLines)
  
  ## SECOND, Remove From "discounts.txt" File, Then "subscriptions.txt" File
  filePath = getFilePath("discounts.txt")
  for i in range(0,2):
    with open(filePath, 'r') as readableFile:
      readableFileLines = readableFile.readlines()
    
    for lineNum,eachLine in enumerate(readableFileLines):
      if not("#" in eachLine) and "User" in eachLine and userName in eachLine:
        readableFileLines.pop(lineNum)
        # Remove Until Discounts For User Are Gone
        while not("User" in readableFileLines[lineNum]):
          readableFileLines.pop(lineNum)
          if lineNum >= len(readableFileLines):
            break
    
    with open(filePath, 'w') as writableFile:
      writableFile.writelines(readableFileLines)
    
    # Set To "subscriptions.txt" In The Second Run
    filePath = getFilePath("subscriptions.txt")
    
  ## THIRD, Remove Any Items That Was In The Cart That Was From That User
  filePath = getFilePath("orderInCart.txt")
  with open(filePath, 'r') as readableFile:
    readableFileLines = readableFile.readlines()
  
  for lineNum,eachLine in enumerate(readableFileLines):
    if not("#" in eachLine) and userName == eachLine.replace("\n",""):
      startVal = lineNum - 1
      readableFileLines.pop(startVal)
      while startVal < len(readableFileLines) and not("Order No" in readableFileLines[startVal]):
        readableFileLines.pop(startVal)
  with open(filePath, 'w') as writableFile:
    writableFile.writelines(readableFileLines)
  # <<Send Data Back To Client>>
  con.send("<USER_DELETED>".encode())
  print(f"User {userName} Has Been Deleted.")


#------------------#
# 4. Get All Users #
#------------------#
def serverADMIN_getAllUsers(con):
  listOfUsers = []
  listOfUsers_String = ""
  # Open "passwd.txt" File To GET Username And Password
  filePath = getFilePath("passwd.txt")
  with open(filePath, 'r') as readableFile:
    readableFileLines = readableFile.readlines()
  
  # GET List Of Users
  userNum = 1
  for eachLine in readableFileLines:
    if not("#" in eachLine) and f"User {userNum}: " in eachLine:
      if not("Admin" in eachLine):
        listOfUsers.append(eachLine.replace(f"User {userNum}: ","").replace("\n",""))
      userNum += 1
  
  # <<Send Data To Client>>
  for eachName in listOfUsers:
    listOfUsers_String += eachName + ","
  listOfUsers_String = listOfUsers_String[:-1]
  con.send(listOfUsers_String.encode())
  print("Grabbing List Of Users.")


#--------------------------------#
# 5. Get Specific User Discounts #
#--------------------------------#
def serverADMIN_getUserDiscounts(userName, con):
  # Grab The Discounts For The User
  filePath = getFilePath("discounts.txt")
  with open(filePath, 'r') as readableFile:
    readableFileLines = readableFile.readlines()
  
  userNum = 1
  keyArr = [] # Allocates The Services In A key:value Pair
  valueArr = []
  for lineNum,eachLine in enumerate(readableFileLines):
    if "#" in eachLine and not(":") in eachLine:
      keyArr.append(eachLine.replace("\n","").replace("# ",""))
    
    if not("#" in eachLine) and "User" in eachLine:
      if f"User {userNum}: {userName}" in eachLine:
        startVal = lineNum + 1
        while startVal < len(readableFileLines) and not("User" in readableFileLines[startVal]):
          valueArr.append(readableFileLines[startVal].replace("\n",""))
          startVal += 1
        break
      userNum += 1
  
  discountsDict = {}
  for num,eachItem in enumerate(keyArr):
    discountsDict[eachItem] = valueArr[num]
  
  discountsDict = pickle.dumps(discountsDict)
  con.send(discountsDict)
  print(f"Grabbing Discounts For User {userName}.")


#------------------------------#
# 6. Upload New User Discounts #
#------------------------------#
def serverADMIN_uploadUserDisc(con):
  discountsDict = pickle.loads(con.recv(4096))
  userName = discountsDict.pop("Username")
  
  # Grab The Location For The Old Discounts For User
  filePath = getFilePath("discounts.txt")
  with open(filePath, 'r') as readableFile:
    readableFileLines = readableFile.readlines()
  
  userNum = 1
  for lineNum, eachLine in enumerate(readableFileLines):
    if not("#" in eachLine) and "User" in eachLine:
      if f"User {userNum}: {userName}" in eachLine:
        startVal = lineNum + 1
        for eachSer in list(discountsDict.keys()):
          readableFileLines[startVal] = f"{discountsDict[eachSer]}\n"
          startVal += 1
        break
      userNum+=1
  
  # Write The Changes To The 'discounts.txt' File
  with open(filePath, 'w') as writeableFile:
    writeableFile.writelines(readableFileLines)
  con.send("<UPDATED_USERDISCOUNTS>".encode())
  print(f"Updated Discounts For User {userName}.")


#----------------------------------------------------#
# 7. Get List Of Users That Requested Reset Password #
#----------------------------------------------------#
def serverADMIN_getUsersResetPass(con):
  # Grab The List Of Users From The "usersForgotPassword.txt" File
  nameOfUsersToResetPass_String = ""
  filePath = getFilePath("usersForgotPassword.txt")
  nameOfUsersToResetPass = []
  with open(filePath, 'r') as readableFile:
    readForgotPassFile = readableFile.readlines()
  
  for eachLine in readForgotPassFile:
    if not("#" in eachLine):
      nameOfUsersToResetPass.append(eachLine.replace("\n",""))
  
  # Determines Whether Any Users To Reset Password
  if len(nameOfUsersToResetPass) != 0:
    nameOfUsersToResetPass_String = "<HAVE_USERSTORESET>"
    for eachItem in nameOfUsersToResetPass:
      nameOfUsersToResetPass_String += eachItem + ","
    nameOfUsersToResetPass_String = nameOfUsersToResetPass_String[:-1]
  else:
    nameOfUsersToResetPass_String = "<NO_USERSTORESET-->"
  
  con.send(nameOfUsersToResetPass_String.encode())
  print("Grabbing List Of Pending Password Resets.")


#---------------------------#
# 8. Reset Password Of User #
#---------------------------#
def serverADMIN_resetPassword(userName, con):
  # Change Password To Default Password Of "Password"
  filePath = getFilePath("passwd.txt")
  with open(filePath, 'r') as readableFile:
    readableFileLines = readableFile.readlines()
  for num,eachLine in enumerate(readableFileLines):
    if not("#" in eachLine) and "User" in eachLine and userName in eachLine:
      readableFileLines[num+1] = "Password"[::-1] + "\n"
      break
  with open(filePath, 'w') as writableFile:
    writableFile.writelines(readableFileLines)
  
  # Remove From "usersForgotPassword.txt" File
  filePath = getFilePath("usersForgotPassword.txt")
  with open(filePath, 'r') as readableFile:
    readableFileLines = readableFile.readlines()
  for lineNum,eachLine in enumerate(readableFileLines):
    if userName == eachLine.replace("\n",""):
      readableFileLines.pop(lineNum)
  filePath = getFilePath("usersForgotPassword.txt")
  with open(filePath, 'w') as writableFile:
    writableFile.writelines(readableFileLines)
  con.send("<UPDATED_USERRESETPASSWORD>".encode())
  print(f"Password Reset Successful For User {userName}.")


#-------------------------#
# 9. Get List Of Services #
#-------------------------#
def serverADMIN_getListOfServices(con):
  # Grab Information From The "services.txt" File
  listOfServices = []
  listOfServices_String = ""
  filePath = getFilePath("services.txt")
  with open(filePath, 'r') as readableFile:
    readableFileLines = readableFile.readlines()
  for eachLine in readableFileLines:
    if not("#" in eachLine):
      listOfServices.append(eachLine.replace("\n",""))
  
  for eachSer in listOfServices:
    listOfServices_String += eachSer + ","
  listOfServices_String = listOfServices_String[:-1]
  con.send(listOfServices_String.encode())
  print("Grab List Of Services.")


#-----------------------------#
# 10. Update List Of Services #
#-----------------------------#
def serverADMIN_updateServices(buf, con):
  listOfServices = buf.split(",")
  for num,eachLine in enumerate(listOfServices):
    listOfServices[num] = f"{eachLine}\n"
  filePath = getFilePath("services.txt")
  with open(filePath, 'r') as readableFile:
    readableFileLines = readableFile.readlines()
  # Update With The New Services
  for lineNum,eachLine in enumerate(readableFileLines):
    if not("#" in eachLine):
      while lineNum < len(readableFileLines):
        readableFileLines.pop(lineNum)
      readableFileLines.extend(listOfServices)
      break
  
  with open(filePath, 'w') as writeableFile:
    writeableFile.writelines(readableFileLines)

  con.send("<UPDATED_LISTOFSERVICES>".encode())
  print("Services File Has Been Updated.")


#-----------------------#
# 11. Add A New Service #
#-----------------------#
def serverADMIN_addNewService(newServiceName, con):
  # Update The "discounts.txt" File First
  filePath = getFilePath("discounts.txt")
  
  for i in range(0,2):    
    ## Determines The Number Of Current Services + Add New Service Name
    noOfServices = 0
    with open(filePath, 'r') as readableFile:
      readableFileLines = readableFile.readlines()
    for lineNum, eachLine in enumerate(readableFileLines):
      if "#" in eachLine and not (":" in eachLine):
        noOfServices += 1
      if not("#" in eachLine):
        readableFileLines.insert(lineNum,f"# {newServiceName}\n")
        break
    if "discounts.txt" in filePath:
      ## Adds New Line Of Discounts For New Service In "discounts.txt" File
      for lineNum, eachLine in enumerate(readableFileLines):
        if not("#" in eachLine) and "User" in eachLine:
          startVal = lineNum + noOfServices + 1
          readableFileLines.insert(startVal, "0\n")
    elif "subscriptions.txt" in filePath:
      ## Adds New Line Of Discounts For New Service In "discounts.txt" File
      for lineNum, eachLine in enumerate(readableFileLines):
        if not("#" in eachLine) and "User" in eachLine:
          startVal = lineNum + noOfServices*2 + 1
          readableFileLines.insert(startVal, "0\n")
          readableFileLines.insert(startVal, "-\n")
    
    with open(filePath, 'w') as writeableFile:
      writeableFile.writelines(readableFileLines)
    
    # Update The "subscriptions.txt" File Second
    filePath = getFilePath("subscriptions.txt")
  con.send("<UPDATED_DISC_SUBS>".encode())
  print("Discounts And Subscriptions Files Have Been Updated.")


#----------------------#
# 12. Delete A Service #
#----------------------#
def serverADMIN_removeService(serviceName,con):
  # Update The "discounts.txt" File First
  filePath = getFilePath("discounts.txt")
  
  for i in range(0,2):
    keyVal = 1
    with open(filePath, 'r') as readableFile:
      readableFileLines = readableFile.readlines()
    
    # Removes From "service"
    for lineNum,eachLine in enumerate(readableFileLines):
      if "#" in eachLine and not(":" in eachLine):
        if f"# {serviceName.title()}\n" == eachLine:
          readableFileLines.pop(lineNum)
          break
        keyVal += 1
    # Determines Whether "discounts.txt" Or "subscriptions.txt" File
    if "discounts.txt" in filePath:
      for lineNum, eachLine in enumerate(readableFileLines):
        if not("#" in eachLine) and "User" in eachLine:
          startVal = lineNum + keyVal
          readableFileLines.pop(startVal)      
    elif "subscriptions.txt" in filePath:
      for lineNum, eachLine in enumerate(readableFileLines):
        if not("#" in eachLine) and "User" in eachLine:
          startVal = lineNum + (keyVal-1)*2 + 1
          readableFileLines.pop(startVal)
          readableFileLines.pop(startVal)
    
    # Write To File
    with open(filePath, 'w') as writeableFile:
      writeableFile.writelines(readableFileLines)
    
    filePath = getFilePath("subscriptions.txt")
  con.send("<UPDATED_DISC_SUBS>".encode())
  print("Discounts And Subscriptions Files Have Been Updated.")


#-----------#
# handler() #
#-----------#
def handler(con):
  # Get List Of Services
  listOfServices = []
  filePath = getFilePath("services.txt")
  with open(filePath, 'r') as serviceAccount:
    serviceAccountLine = serviceAccount.readlines()
    for line in serviceAccountLine:
      # ADD Service And Their Cost To List of Services
      if not("#" in line):
        listOfServices.append(line.replace('\n',''))
  
  try:
    buf = con.recv(24).decode()          # decode the bytes into printable str
    if len(buf) > 0:
      #--------------------------------------#
      # Determines Input Sent By User Client #
      #--------------------------------------#
      # 1. User Choose Category 
      if "<USER_CHOOSE_CATEGORY-->" in buf:
        buf = con.recv(255).decode()
        listOfServices = server_CategoryOption(con, buf)
      # 2. User Request List Of Available Services
      elif "<DISPLAY_LISTOFSERVICES>" in buf:
        buf = con.recv(255).decode()
        server_SearchService(buf, listOfServices, con)
      # 3. User Request Price Of Service
      elif "<USER_GETPRICEOFSERVICE>" in buf:
        buf = con.recv(255).decode()
        print(f"Get Price For Service - {buf}")
        for lineNum,eachItem in enumerate(listOfServices):
          if eachItem.title() == buf:
            priceOfItem = listOfServices[lineNum+1]
            break
        con.send(priceOfItem.encode())
      # 4. User Request Previous Order Number
      elif "<USER_GETPREVIOUSORDER->" in buf:
        buf = con.recv(255).decode()
        server_RetrievePreviousOrder(buf, con)
      # 5. User Request Payment Info
      elif "<USER_GETBUSINESSINFO-->" in buf:
        server_GenerateInvoiceInfo(con)
      # 6. User Confirmed Payment
      elif "<USER_CONFIRMPAYMENT--->" in buf:
        server_MakePayment(listOfServices, con)
      # 7. User Confirmed Reset Password
      elif "<USER_CHANGEPASSWORD--->" in buf:
        buf = con.recv(255).decode()
        server_ChangePassword(buf, con)
      # 8. User Confirmed Delete Account
      elif "<USER_DELETEACCOUNT---->" in buf:
        buf = con.recv(255).decode()
        server_PendingDeleteAccount(buf, con)
      # 9. User Leave ESP And Save Cart
      elif "<USER_SAVECART--------->" in buf:
        server_leavingESP(con)
      #---------------------------------------#
      # Determines Input Sent By Admin Client #
      #---------------------------------------#
      # 1. Validate Admin Credentials
      elif "<ADMIN_VALIDATEUSER---->" in buf:
        buf = con.recv(255).decode()
        serverADMIN_checkAdmin(buf, con)
      # 2. Get List Of Users Pending Deletion 
      elif "<ADMIN_GETUSERSTODELETE>" in buf:
        serverADMIN_getUsersPendingDeletion(con)
      # 3. Delete User
      elif "<ADMIN_DELETEUSER------>" in buf:
        buf = con.recv(255).decode()
        serverADMIN_deleteUser(buf, con)
      # 4. Get List Of Users
      elif "<ADMIN_GETALLUSERS----->" in buf:
        serverADMIN_getAllUsers(con)
      # 5. Get Specific User Discounts
      elif "<ADMIN_GETUSERDISCOUNTS>" in buf:
        buf = con.recv(255).decode()
        serverADMIN_getUserDiscounts(buf, con)
      # 6. Save New User Discounts
      elif "<ADMIN_UPLOADNEWDISC--->" in buf:
        serverADMIN_uploadUserDisc(con)
      # 7. Get List Of Users Pending Reset Password
      elif "<ADMIN_GETUSERSTORESET->" in buf:
        serverADMIN_getUsersResetPass(con)
      # 8. Reset User Password
      elif "<ADMIN_RESETPASSWORD--->" in buf:
        buf = con.recv(255).decode()
        serverADMIN_resetPassword(buf, con)
      # 9. Get List Of Services
      elif "<ADMIN_GETLISTOFSERVICE>" in buf:
        serverADMIN_getListOfServices(con)
      # 10. Save ALL New Services
      elif "<ADMIN_UPDATESERVICES-->" in buf:
        buf = con.recv(255).decode()
        serverADMIN_updateServices(buf, con)
      # 11. Add A New Service
      elif "<ADMIN_ADDNEWSERVICE--->" in buf:
        buf = con.recv(255).decode()
        serverADMIN_addNewService(buf, con)
      # 12. Delete A Service
      elif "<ADMIN_DELETESERVICE--->" in buf:
        buf = con.recv(255).decode()
        serverADMIN_removeService(buf,con)
    else:
      return                              # return immediately and no need to close the con. (There is None)
    con.close()
  except:
    print(WindowsError)
  # print ("handler for {} is terminated".format(str(client_addr)))
  print(f"Closed connection for: {address[0]}:{address[1]}\n")

# main program starts here
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = 'localhost'
port = 8089
ThreadCount = 0
try:
  serversocket.bind((host, port))
except socket.error as e:
  print(str(e))

print("Server starts listening... ")
serversocket.listen(5)        # become a server socket, maximum 5 pending connections

while True:
  Client, address = serversocket.accept()
  print('Connected to: ' + address[0] + ':' + str(address[1]))
  start_new_thread(handler, (Client, ))
  ThreadCount += 1
  print('Thread Number: ' + str(ThreadCount))
  print(f"Active threads: {threading.activeCount() - 1 }")

serversocket.close()
print("Server is halted.")