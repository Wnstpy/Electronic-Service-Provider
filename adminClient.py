'''
Name:               Seow Wee Hau Winston
Name Of File:       admins.py

Input-Output Files: None - Makes Request To Server

#-----------------------------------------------------------#
This file is made for START ADMIN PROGRAM. Each function in
this file is meant solely for the admin options.
#-----------------------------------------------------------#
'''
import os
import msvcrt
import socket
import pickle

#----------------------------------#
#  Generate Asterisks For Password #
#----------------------------------#
def getPassword(passWord="Enter Admin's Password: ", stream=None):
  for c in passWord:
    msvcrt.putwch(c)
  passWord = ""
  while True:
    eachVal = msvcrt.getwch()
    # Press "ENTER"
    if eachVal == "\r" or eachVal == "\n":
      break
    # Press "Ctrl + C"
    if eachVal == "\003":
      raise KeyboardInterrupt
    # Press "BACKSPACE"
    if eachVal == "\b":
      # IF Length Longer Than Zero
      if len(passWord) > 0:
        passWord = passWord[:-1]
        msvcrt.putwch("\b")
        msvcrt.putwch(" ")
        msvcrt.putwch("\b")
    # ELSE Other Input
    else:
      passWord = passWord + eachVal
      msvcrt.putwch("*")
  msvcrt.putwch("\n")
  return passWord


#-------------------------------#
# Send/Receive Data From Server #
#-------------------------------#
def sendRecvDataFromServer(dataToSend, optionNum = 1, secondDataToSend=""):
  clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  host = 'localhost'
  clientSocket.connect((host, 8089))
  clientSocket.send(dataToSend)
  # Option 1: Receive Data From Server
  if optionNum == 1:
    dataToRecv = clientSocket.recv(255).decode()
    clientSocket.close()
  # Option 2: Receive Pickle From Server
  elif optionNum == 2:
    dataToRecv = clientSocket.recv(4096)
    clientSocket.close()
  # Option 3: Send Second Data To Server + Receive Data From Server
  elif optionNum == 3:
    clientSocket.send(secondDataToSend)
    dataToRecv = clientSocket.recv(255).decode()
    clientSocket.close()
  return dataToRecv


##############################################
  # Suboption Menu 1: After Manage Users [1]
##############################################
def subOptionSelection():
  leaveSubProgram = False
  subOptionMenu = ["Delete Registered User", "Modify User Discounts", "Reset User Password", "Return To Main Menu"]
  subOptionSelectionInput = ""
  
  listOfUsers_String = sendRecvDataFromServer("<ADMIN_GETALLUSERS----->".encode())
  listOfUsers = listOfUsers_String.split(",")
  
  while leaveSubProgram == False:
    print("\n#-----------------#")
    print(" Suboption Menu 1 ")
    print("#-----------------#")
    [print(f"\t{num}. {option}") for num,option in enumerate(subOptionMenu,1)]
    
    
    # Validate Option First
    while True:
      try:
        subOptionSelectionInput = int(input("\nPlease Choose An Option: ").strip())
        if userOption < 1 or userOption > 4:
          print("Please Enter A Valid Number!")
        else:
          break
      except ValueError:
        print("Please Enter An Integer!")
      
    if subOptionSelectionInput == 1:
      listOfUsers = deleteUser(listOfUsers)
    elif subOptionSelectionInput == 2:
      changeUserDiscounts(listOfUsers)
    elif subOptionSelectionInput == 3:
      resetUserPass()
    elif subOptionSelectionInput == 4:
      leaveSubProgram = True
    else:
      print("Please Enter A Valid Option!")
    print("\nReturning To Suboption Menu 1...\n")


#******************************************#
# Suboption Menu 1: Delete User [Option 1] #
#******************************************#
def deleteUser(listOfUsers):
  isValidUserName = False
  nameOfUsersToDel = sendRecvDataFromServer("<ADMIN_GETUSERSTODELETE>".encode())
  print("=-----------------------------------=")
  print("       Users Pending Deletion        ")
  print("=-----------------------------------=")
  if "<HAVE_USERS>" in nameOfUsersToDel:
    nameOfUsersToDel = nameOfUsersToDel[12:]
    nameOfUsersToDel = nameOfUsersToDel.split(",")
    
    [print(f"{num}. {username}") for num,username in enumerate(nameOfUsersToDel,1)]  
    print("=-----------------------------------=")  
    # Checks If Admin Input Valid Username
    while isValidUserName == False:
      try:
        userName = input("Please Enter Name Of User To Delete: ").strip().title()
        for eachName in nameOfUsersToDel:
          if userName == eachName.title():
            isValidUserName = True
            break
        # If Admin Entered A Invalid Username
        if isValidUserName == False:
          print(f"There Are No Users With The Name {userName}.")
          break
      except:
        print("Please Enter A Valid Username")
    
    if isValidUserName:
      # Double Confirm To Delete User
      while True:
        doubleConfirm = input(f"Are You Sure To Delete User {userName} (Y/N): ").strip().capitalize()
        if doubleConfirm == "Y": # Confirm Deletion
          for num,eachName in enumerate(listOfUsers):
            if eachName.title() == userName.title():
              listOfUsers.pop(num)
              break
          dataFromServer = sendRecvDataFromServer(f"<ADMIN_DELETEUSER------>{userName}".encode())
          if dataFromServer == "<USER_DELETED>":
            print(f"User {userName} Has Been Deleted.")
            break
          else:
            print(f"User {userName} Has Not Been Deleted.")
        elif doubleConfirm == "N": # Cancel Deletion
          print(f"Cancelling Deletion of User {userName}")
          break
        else:
          print("Please Enter A Valid Option!")
  elif "<NO_USERS-->" in nameOfUsersToDel:
    print("-"*37)
    print("No Pending Users To Delete.")
  print("-"*37)
  return listOfUsers


#***************************************************#
# Suboption Menu 1: Modify User Discounts [Option 2]#
#***************************************************#
def changeUserDiscounts(listOfUsers):
  # Display List Of Usernames
  print("-"*25)
  print("No.\tUsername")
  print("-"*25)
  [print(f"{num}.\t{eachName}") for num, eachName in enumerate(listOfUsers,1)]
  print("-"*25)
  
  # Check Username
  userName = ""
  isValidUserName = False
  print("=----------------------=")
  print(" Modify User Discounts ")
  print("=----------------------=")
  
  while isValidUserName == False:
    userName = input("Enter A Username To Change Their Discounts: ").strip().title()
    for eachName in listOfUsers:
      if userName == eachName:
        isValidUserName = True
        break
    if isValidUserName == False:
      # If Username Is Not Found
      print("Please Enter A Valid Username!")
  
  discountsDict = sendRecvDataFromServer(f"<ADMIN_GETUSERDISCOUNTS>{userName}".encode(), 2)
  discountsDict = pickle.loads(discountsDict)
  
  # Username Is Validated And Discounts Have Been Retrieved
  while True:
    isValidDiscountAmt = False
    print("-"*50)
    print(f"Showing User {userName} Discounts:")
    print("-"*50)
    print("Service Name:\t\tDiscount(0 - 1)")
    [print(f"{eachSer:16}\t{discountsDict[eachSer]}") for num,eachSer in enumerate(list(discountsDict.keys()),1)]
    print("-"*50)
    
    discountName = input("Enter A Discount Name To Modify or ENTER To Leave: ").strip().title()
    
    # IF "ENTER"
    if discountName == "":
      break
    
    # IF Entered A Discount Name
    for eachSer in list(discountsDict.keys()):
      if discountName == eachSer:
        while isValidDiscountAmt == False:
          discountAmt = ''
          try:
            discountAmt = input(f"Enter A Discount Value For {discountName}: ").strip()
            discountAmt = float(discountAmt)
            if discountAmt > 1 or discountAmt < 0:
              print(f"Please Enter A Value From 0 - 1")
            else:
              discountsDict[eachSer] = str(discountAmt)
              isValidDiscountAmt = True
          except:
            print("Please Enter A Valid Discount Amount")
        break
    if isValidDiscountAmt == False:
      print(f"No Service Of Name {discountName} Found.")
  # <<Sends Data To Server To Save New Discounts For User>>
  discountsDict["Username"] = userName
  discountsDict = pickle.dumps(discountsDict)
  isUpdated = sendRecvDataFromServer("<ADMIN_UPLOADNEWDISC--->".encode(), 3, discountsDict)
  if isUpdated == "<UPDATED_USERDISCOUNTS>":
    print(f"Discounts For User {userName} Has Been Updated.")


#**************************************************#
# Suboption Menu 1: Reset User Password [Option 3] #
#**************************************************#
def resetUserPass():
  nameofUsersToReset = sendRecvDataFromServer("<ADMIN_GETUSERSTORESET->".encode())
  print("=-----------------------------------=")
  print("       Reset User Password        ")
  print("=-----------------------------------=")
  if "<HAVE_USERSTORESET>" in nameofUsersToReset:
    nameofUsersToReset = nameofUsersToReset[19:]
    nameofUsersToReset = nameofUsersToReset.split(",")
    
    [print(f"{num}. {user}") for num,user in enumerate(nameofUsersToReset,1)]
    print("-"*37)
    
    userName = input("Enter A Username: ").strip().capitalize()
    
    isValidUserName = False
    for eachName in nameofUsersToReset:
      if userName == eachName:
        isValidUserName = True
    
    if isValidUserName:
      hasResetPassword = sendRecvDataFromServer(f"<ADMIN_RESETPASSWORD--->{userName}".encode())
      if hasResetPassword == "<UPDATED_USERRESETPASSWORD>":
        print(f"The Password For User {userName} Has Been Reset.")
    else:
      print(f"There Are No Users With The Name {userName}.")
  elif "<NO_USERSTORESET-->" in nameofUsersToReset:
    print("-"*37)
    print("No Pending Users To Reset Password.")
    print("-"*37)


#*********************************************#
# Suboption Menu 2: After Manage Services [2] #
#*********************************************#
def subOption2Selection():
  leaveSub2Program = False
  subOption2Menu = ["Add New Service", "Delete Current Service", "Modify Service", "Return To Main Menu"]
  
  listOfServices = sendRecvDataFromServer("<ADMIN_GETLISTOFSERVICE>".encode())
  listOfServices = listOfServices.split(",")
  while leaveSub2Program == False:
    print("\n=-----------------=")
    print(" Suboption Menu 2 ")
    print("=-----------------=")
    [print(f"\t{num}. {option}") for num,option in enumerate(subOption2Menu,1)]
    print("-"*20)
    
    # Validate Option First
    while True:
      try:
        subOption2SelectionInput = int(input("\nPlease Choose An Option: ").strip())
        if userOption < 1 or userOption > 4:
          print("Please Enter A Valid Number!")
        else:
          break
      except ValueError:
        print("Please Enter An Integer!")
      
    # Determine Which Option
    if subOption2SelectionInput in range(1,4):
      if subOption2SelectionInput == 1:
          listOfServices = addService(listOfServices)
      elif subOption2SelectionInput == 2:
          listOfServices = deleteService(listOfServices)
      elif subOption2SelectionInput == 3:
          listOfServices = modifyExistingService(listOfServices)
      
      # Shows A Final Copy Of The List Of Services
      displayListOfServices(listOfServices)
    elif subOption2SelectionInput == 4:
      leaveSub2Program = True
    else:
      print("Please Enter A Valid Option!")


#------------------------#
# Shows List Of Services #
#------------------------#
def displayListOfServices(listOfServices):
  # Print Current List Of Services
  print("="*50)
  print("Current Services:\t\t\tCost ($):")
  print("="*50)
  for lineNum in range(0,len(listOfServices),2):
    print(f"{listOfServices[lineNum].title():30}\t\t{listOfServices[lineNum+1]}")
  print("="*50)


#**********************************************#
# Suboption Menu 2: Add New Service [Option 1] #
#**********************************************#
def addService(listOfServices):
  print("=----------------------=")
  print("   Adding New Service  ")
  print("=----------------------=")
  while True:
    isValidAmt = False
    isValidServ = True
    displayListOfServices(listOfServices)
    # Add Service Name
    newServiceName = input("Enter New Service Name Or ENTER To Leave: ").title().strip()
    # IF "ENTER", Leave
    if newServiceName == "":
      break
    # IF Service Name
    elif len(newServiceName) > 20:
      print("Length Of Service Name Is Too Long!\nPlease Shorten It To Lesser Than 20 Characters.")
    else:
      for eachServ in listOfServices:
        if newServiceName.lower() == eachServ:
          isValidServ = False
      if isValidServ:
        while isValidAmt == False:
          try:
            newServiceAmt = input("Enter New Service Cost: $")
            newServiceAmt = int(newServiceAmt.strip())
            isValidAmt = True
          except:
            print("Please Enter An Integer!")
        
        # Add To List Of Services
        listOfServices.append(newServiceName.lower())
        listOfServices.append(newServiceAmt)
        
        # <<Send Data To Server To Update The "discounts.txt" And "subscriptions.txt" Files
        dataFromServer = sendRecvDataFromServer(f"<ADMIN_ADDNEWSERVICE--->{newServiceName.title()}".encode())
        if dataFromServer == "<UPDATED_DISC_SUBS>":
          print("Adding New Service...")
        
      else:
          print("Please Enter A Service Name That Is Not Used.")
      print("-"*40)
  # <<Send Data To Server To Update Only If FINISHED ADDING SERVICES>>
  dataToSendToServer = "<ADMIN_UPDATESERVICES-->"
  for eachItem in listOfServices:
    dataToSendToServer += str(eachItem) + ","
  dataToSendToServer = dataToSendToServer[:-1]
  dataFromServer = sendRecvDataFromServer(dataToSendToServer.encode())
  if dataFromServer == "<UPDATED_LISTOFSERVICES>":
    print("Service File Has Been Updated.")
  
  return listOfServices


#*****************************************************#
# Suboption Menu 2: Delete Current Service [Option 2] #
#*****************************************************#
def deleteService(listOfServices):
  print("=----------------------=")
  print(" Delete Current Service ")
  print("=----------------------=")
  while True:
    isValidServName = False
    displayListOfServices(listOfServices)
    # Service Name To Delete
    rmServiceName = input("Enter Service Name To Delete Or ENTER To Leave: ").title().strip()
    if rmServiceName == "":
      break
    else:
      for lineNum in range(0,len(listOfServices),2):
        if rmServiceName.lower() == listOfServices[lineNum].lower():
          # Removes From listOfServices, Tabulated Into "services.txt" File Later
          listOfServices.pop(lineNum)
          listOfServices.pop(lineNum)
          
          # <<Send Data To Server To Update The "discounts.txt" And "subscriptions.txt" Files
          dataFromServer = sendRecvDataFromServer(f"<ADMIN_DELETESERVICE--->{rmServiceName.title()}".encode())
          if dataFromServer == "<UPDATED_DISC_SUBS>":
            print(f"Removing Service {rmServiceName}")
          isValidServName = True
          break
      if isValidServName == False:
        print("Please Enter A Valid Service Name!")
      print("-"*40)
  
  # <<Send Data To Server To Update Only If FINISHED ADDING SERVICES>>
  dataToSendToServer = "<ADMIN_UPDATESERVICES-->"
  for eachItem in listOfServices:
    dataToSendToServer += str(eachItem) + ","
  dataToSendToServer = dataToSendToServer[:-1]
  dataFromServer = sendRecvDataFromServer(dataToSendToServer.encode())
  if dataFromServer == "<UPDATED_LISTOFSERVICES>":
    print("Service File Has Been Updated.")
  return listOfServices


#*****************************************************#
# Suboption Menu 2: Modify Current Service [Option 3] #
#*****************************************************#
def modifyExistingService(listOfServices):
  print("=----------------------=")
  print(" Modify Current Service ")
  print("=----------------------=")
  while True:
    isValidServName = False
    print("\n")
    displayListOfServices(listOfServices)
    # Retrieve Service Name
    chgServiceName = input("Enter Service Name To Modify Or ENTER To Leave: ").title()
    chgServiceName = chgServiceName.strip()
    
    # Check Input
    if chgServiceName == "":
      break
    else:
      for lineNum,eachLine in enumerate(listOfServices):
        if chgServiceName.lower() == eachLine:
          # Request For Valid Cost Change in listOfServices
          while True:
            newCost = input(f"Enter A New Cost For {chgServiceName}: $")
            newCost = newCost.strip()
            if newCost.isnumeric():
              break
            else:
              print("Please Enter An Integer!")
          listOfServices[lineNum+1] = f"{newCost}"
          
          stringToSendServer = "<ADMIN_UPDATESERVICES-->"
          for eachItem in listOfServices:
            stringToSendServer += eachItem + ","
          stringToSendServer = stringToSendServer[:-1]
          dataFromServer = sendRecvDataFromServer(stringToSendServer.encode())
          if dataFromServer == "<UPDATED_LISTOFSERVICES>":
            print("Service File Has Been Updated.")
          isValidServName = True
          break
      if isValidServName == False:
        print("Please Enter A Valid Service Name!")
  return listOfServices


# <----------------------------------> #
#                                      #
#              Start Program           #
#                                      #
#                                      #
# <----------------------------------> #
# Start Program
try:
  print("-=============================-")
  print("Starting Up...")
  
  #-------------------#
  # 1. Validate Admin #
  #-------------------#
  # Validates Input
  isValidUser = False
  while isValidUser == False:
    userName = input("Enter Admin's Username: ").strip().title()
    userPass = getPassword()
    
    stringToSendServer = f"<ADMIN_VALIDATEUSER---->{userName},{userPass}"
    validAdmin = sendRecvDataFromServer(stringToSendServer.encode())
    if validAdmin == "<VALIDATED_ADMIN>":
      isValidUser = True
    else:
      print("Invalid Credentials")
  
  #--------------#
  # 2. Main Menu #
  #--------------#
  # GET List Of Options
  listOfOptions = ["Manage User", "Manange Services", "Exit ESP"]
  userOption = ""
  
  print("-" * 70)
  print(f"\tWelcome {userName} to Winston's (E)Service Provider:")
  print("-" * 70)
  
  #-------------------#
  # Main Menu Options #
  #-------------------#
  leaveProgram = False
  while leaveProgram == False:
    # List All Options
    print("-"*25)
    print("List Of Options:")
    print("-"*25)
    [print(f"{num}. {option}") for num,option in enumerate(listOfOptions, 1)]
    
    # Validate Option First
    while True:
      try:
        userOption = int(input("\nPlease Choose An Option: ").strip())
        if userOption < 1 or userOption > 3:
          print("Please Enter A Valid Number!")
        else:
          break
      except ValueError:
        print("Please Enter An Integer!")
    
    if userOption == 1:
      subOptionSelection()
    elif userOption == 2:
      subOption2Selection()
    elif userOption == 3:
      print("Leaving Admin Client Program...")
      leaveProgram = True
    # leaveProgram = optionSelection(userOption, listOfUsers, leaveProgram)
except WindowsError:
  print("The ESP Server May Be Down For Maintenance.")
  print("-=========================================-")