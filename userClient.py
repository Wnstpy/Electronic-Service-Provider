'''
Name:               Seow Wee Hau Winston
Name Of File:       userClient.py

# Input-Output Files: None - Makes Request To Server

# #-----------------------------------------------------------#
# This file is made to START USER PROGRAM. It validates
# whether the user is a registered user or new user,
# before validating and starting the program.
# #-----------------------------------------------------------#
'''

import msvcrt
import socket
import re
import pickle
import time
import datetime
from datetime import date

#----------------------------------#
#  Generate Asterisks For Password #
#----------------------------------#
def getPassword(passWord='Enter Password: ', stream=None):
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
def sendRecvDataFromServer(dataToSend, secondDataToSend = "", optionNum = 1, amtToRecv = 255):
  clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  host = 'localhost'
  clientSocket.connect((host, 8089))
  # Option 4: Only Receive Data From Server
  if amtToRecv != 255:
    clientSocket.send(dataToSend)
    pickleData = ""
    dataToRecv = clientSocket.recv(amtToRecv).decode()
    if dataToRecv == "<VALIDATED_CREDENTIALS>":
      pickleData = clientSocket.recv(4096)
    elif dataToRecv == "<USERNAME_VALID>":
      pickleData = clientSocket.recv(23)
      pickleData = clientSocket.recv(4096)
    return dataToRecv, pickleData
  else:
    clientSocket.send(dataToSend)
    # Option 1: Receive Data From Server
    if optionNum == 1:
      dataToRecv = clientSocket.recv(amtToRecv).decode()
      clientSocket.close()
      return dataToRecv
    # Option 2: Send Second Data To Server
    elif optionNum == 2:
      clientSocket.send(secondDataToSend)
      clientSocket.close()
    # Option 3: Send Second Data To Server + Receive Data From Server
    elif optionNum == 3:
      clientSocket.send(secondDataToSend)
      dataToRecv = clientSocket.recv(amtToRecv).decode()
      clientSocket.close()
      return dataToRecv


#======================================#
# Main Menu: Search Service [Option 1] #
#======================================#
def client_SearchService(registeredUser, listOfServices, leaveProgram):
  nameOfServiceToSearch = input("Please Enter Name Of Service: ")
  # If User Wants To Display All Services
  if nameOfServiceToSearch == "":
    nameOfServiceToSearch = "<DISPLAYALLSERVICES>"
  
  # <<Send nameOfServiceToSearch To Server>>
  nameOfServiceToSearch = f"<DISPLAY_LISTOFSERVICES>{nameOfServiceToSearch}".encode()
  availableServices = sendRecvDataFromServer(nameOfServiceToSearch)
  if availableServices == "<NOAVAILABLESERVICES>":
    print("No Services Found!")
  else:
    availableServices = availableServices.split(',')
    print("================")
    print("Service(s) Found")
    print("================")
    [print(f"{num}. {eachItem}") for num,eachItem in enumerate(availableServices, 1)]
  
  # subOptionSelection Function()
  leaveSubProgram = False
  while leaveSubProgram == False:
    leaveSubProgram, leaveProgram = subOptionSelection(registeredUser, leaveSubProgram, availableServices, listOfServices, leaveProgram)
  
  return leaveProgram


#********************************************#
# Suboption Menu 1: After Search Service [1] #
#********************************************#
def subOptionSelection(registeredUser, leaveSubProgram, availableServices, listOfServices, leaveProgram):
  # SubOptions To Determine User Choice
  subOptions = ["Add To Cart (No.)", "Search Again", "View Cart", "Return To Main Menu"]
  userSubOptionInput = ''
  print("\n=--------------=")
  print("Suboption Menu 1:")
  print("=--------------=")
  [print(f"\t{num}. {subOption}") for num,subOption in enumerate(subOptions, 1)]
  
  # VALIDATE userSubOptionInput is Integer
  while userSubOptionInput.isnumeric() == False:
    userSubOptionInput = input("\n\tEnter A Number: ")
    print("Processing Input...")
    time.sleep(1)
  userSubOptionInput = int(userSubOptionInput)
  
  #- Determine Suboption Chosen -#
  # Suboption 1: Add Items To Cart
  if userSubOptionInput == 1:
    addToCart(availableServices, registeredUser)
  # Suboption 2: Search Again
  elif userSubOptionInput == 2:
    leaveProgram = client_SearchService(registeredUser, listOfServices, leaveProgram)
    leaveSubProgram = True
  # Suboption 3: View Cart
  elif userSubOptionInput == 3:
    leaveProgram = client_ViewCart(registeredUser, listOfServices, leaveProgram)
    leaveSubProgram = True
  # Suboption 4: Return To Main Menu
  elif userSubOptionInput == 4:
    leaveSubProgram = True
  else:
    print("Please Enter A Valid Option!")
  return leaveSubProgram, leaveProgram


#******************************************#
# Suboption Menu 1: Add To Cart [Option 1] #
#******************************************#
def addToCart(availableServices, registeredUser):
  if len(availableServices) == 0 or availableServices == "<NOAVAILABLESERVICES>":
    print("\nNo Services Available!")
  else:
    stopAddingToCart = False
    while stopAddingToCart == False:
      stopAddingToCart = registeredUser.addingServices(stopAddingToCart, availableServices)


#=================================#
# Main Menu: View Cart [Option 2] #
#=================================#
def client_ViewCart(registeredUser, listOfServices, leaveProgram):
  # Determine The Name Of Services & Their Quantity
  for i in range(0,len(listOfServices)):
    serviceKey = listOfServices[i].title()
    serviceValue = 0
    # Check Quantity For Each Different Service
    for eachEle in registeredUser.myCart:
      if eachEle == serviceKey:
        serviceValue += 1
    # IF No Quantity For Service
    if serviceValue > 0:
      registeredUser.myCartDict[serviceKey] = serviceValue
  # SHOW Amount To User
  print("Grabbing Cart...")
  time.sleep(1)
  print("----------------------------=Current Cart:=----------------------------")
  print("Name Of Service:\tQuantity\tDiscount\tCost")
  # Finds The Cost Of Service
  leaveSub2Program = False
  totalCost = 0
  # For Each Service
  for serviceName in registeredUser.myCartDict.keys():
    # RESET Cost Of Service
    costOfService = 0
    for eachEle in listOfServices:
      if eachEle.title() == serviceName:
        getPriceOfService = f"<USER_GETPRICEOFSERVICE>{serviceName}".encode()
        costOfService = int(sendRecvDataFromServer(getPriceOfService))
        break
    # GET The Value With Quantity & Discount
    costValue = costOfService * registeredUser.myCartDict[serviceName] * (1 - registeredUser.discounts[serviceName])
    discountPer = f"{registeredUser.discounts[serviceName] * 100}%"
    # Set The Cost To The Same Index In myCartCost Dictionary
    registeredUser.myCartCost[list(registeredUser.myCartDict).index(serviceName)] = costValue
    print(f"{serviceName:16}\t{registeredUser.myCartDict[serviceName]}\t\t{discountPer}\t\t{costValue:.2f}")
    totalCost += costValue
  print(f"Total Cost: ${totalCost:.2f}")
  print("-"*71)
  time.sleep(1)
  # Executes Sub Menu 2
  while leaveSub2Program == False:
    leaveSub2Program, leaveProgram = subOption2Selection(registeredUser, leaveSub2Program, listOfServices, leaveProgram)
  return leaveProgram


#***************************************#
# Suboption Menu 2: After View Cart [2] #
#***************************************#
def subOption2Selection(registeredUser, leaveSub2Program, listOfServices, leaveProgram):
  userSubOption2Input = ''
  subOptions2 = ["Remove A Service", "Retrieve Order From Previous Session", "Check Out/Payment", "Return To Main Menu"]
  print("\n=--------------=")
  print("Suboption Menu 2:")
  print("=--------------=")
  [print(f"\t{num}. {option}") for num,option in enumerate(subOptions2, 1)]
  print("="*71)
  while userSubOption2Input.isnumeric() == False:
    userSubOption2Input = input("Enter An Suboption No.: ")
  userSubOption2Input = int(userSubOption2Input)
  print("Processing Input...")
  #- Determine Suboption Chosen -#
  # Suboption 1: Remove Service From Cart
  if userSubOption2Input == 1:
    removeService(registeredUser)
  # Suboption 2: Retrieve Order From Previous Session
  elif userSubOption2Input == 2:
    leaveProgram = retrievePreviousOrder(registeredUser, listOfServices, leaveProgram)
    leaveSub2Program = True
  # Suboption 3: Proceed To Payment
  elif userSubOption2Input == 3:
    leaveProgram = orderPayment(registeredUser, listOfServices, leaveProgram)
    leaveSub2Program = True
  # Suboption 4: Return To Main Menu
  elif userSubOption2Input == 4:
    leaveSub2Program = True
  return leaveSub2Program, leaveProgram


#*******************************************************#
# Suboption Menu 2: Remove Service From Cart [Option 1] #
#*******************************************************#
def removeService(registeredUser):
  possibleServNames = []
  isValidServ = isValidQuantity = False
  removeServiceName = ''
  
  print("-"*35)
  print("Remove Service:")
  removeServiceName = input("Enter Service Name (To Be Removed): ").title().strip()
  print("Processing Input...")
  
  # Provide Alternatives
  for eachSer in registeredUser.myCartDict.keys():
    if removeServiceName in eachSer:
      possibleServNames.append(eachSer)
  
  # Check IF Valid Service
  for eachSer in registeredUser.myCartDict.keys():
    if removeServiceName == eachSer:
      isValidServ = True
  
  # IF Service Name is Invalid, Provide Alternatives
  if isValidServ == False:
    print(f"No Service With Name - {removeServiceName}")
    if len(possibleServNames) != 0:
      print(f"Did You Mean: ")
      [print(f"{num}. {eachSer}", end="\n\n") for num,eachSer in enumerate(possibleServNames, 1)]
    else:
      print("No Suggestions Available.\n")
  
  # ELSE Request Quantity Of Service To Remove
  else:
    while isValidQuantity == False:
      removeServiceValue = ''
      while removeServiceValue.isnumeric() == False:
        removeServiceValue = input("Enter Quantity For Service (To Be Removed): ")
      removeServiceValue = int(removeServiceValue)
      time.sleep(1)
      
      # IF Value Greater Than That In Cart
      if removeServiceValue > registeredUser.myCartDict[removeServiceName]:
        print(f"Only Quantity Of ({registeredUser.myCartDict[removeServiceName]}) In Your Cart!")
      else:
        indexVal = list(registeredUser.myCartDict.keys()).index(removeServiceName)
        # IF Value Is Same Than That In Cart
        if removeServiceValue == registeredUser.myCartDict[removeServiceName]:
          registeredUser.myCartDict.pop(removeServiceName)
          registeredUser.myCartCost.pop(indexVal)
          isValidQuantity = True
          # Removes Service In myCart List Also
          registeredUser.myCart = []
          for eachSer in registeredUser.myCartDict:
            for i in range(registeredUser.myCartDict[eachSer]): 
              registeredUser.myCart.append(eachSer)
        # IF Value is Lesser Than That In Cart
        else:
          registeredUser.myCartDict[removeServiceName] -= removeServiceValue
          registeredUser.myCartCost[indexVal] = registeredUser.myCartCost[indexVal] / (registeredUser.myCartDict[removeServiceName] + removeServiceValue) * registeredUser.myCartDict[removeServiceName]
          isValidQuantity = True
          # Removes Quantity Of Service in myCart List Also
          registeredUser.myCart = []
          for eachSer in registeredUser.myCartDict:
            for i in range(registeredUser.myCartDict[eachSer]): 
              registeredUser.myCart.append(eachSer)
  
  print("Loading Cart...")
  time.sleep(1)
  print("----------------=Current Cart:=----------------")
  print("Name Of Service:\tQuantity")
  # For Each Service
  for serviceName in registeredUser.myCartDict.keys():
    print(f"{serviceName:16}\t{registeredUser.myCartDict[serviceName]}")
  print("-"*47)
  print("="*71)


#*******************************************************************#
# Suboption Menu 2: Retrieve Order From Previous Session [Option 2]
#*******************************************************************#
def retrievePreviousOrder(registeredUser, listOfServices, leaveProgram):
  orderNo = input("Enter Order Number: ")
  print("Loading Order...")
  
  # <<Send orderNo And userName To Server>>
  retrievePreviousOrder_Message = f"<USER_GETPREVIOUSORDER->{orderNo},{registeredUser.userName}"
  dataFromServer = sendRecvDataFromServer(retrievePreviousOrder_Message.encode())
  # <<Receive stringToSendClient From Server>>
  if not("<NOORDER>" in dataFromServer):
    dataFromServer = dataFromServer.split(",")
    registeredUser.myCart= []
    registeredUser.myCartDict = {}
    for eachItem in dataFromServer:
      registeredUser.myCart.append(eachItem) # Adds Each New Service
    print("Order Collected!")
    registeredUser.cartOrderNo = orderNo
    leaveProgram = client_ViewCart(registeredUser, listOfServices, leaveProgram)
  else:
    print("Sorry, This Order Does Not Exist!", end="\n\n")
  return leaveProgram


#==========================================#
# Main Menu: Check Out/ Payment [Option 3] #
#==========================================#
def orderPayment(registeredUser, listOfServices, leaveProgram):
  # Validate IF Anything In Cart
  if len(registeredUser.myCart) == 0:
    print("Nothing In Cart!\n")
  # IF There Are Item(s)
  else:
    # Check If myCartDict == {}, Means Never Viewed Cart Before Proceeding To Payment
    if registeredUser.myCartDict == {}:
      # Determine The Name Of Services & Their Quantity
      for i in range(0,len(listOfServices)):
        serviceKey = listOfServices[i].title()
        serviceValue = 0
        # Check Quantity For Each Different Service
        for eachEle in registeredUser.myCart:
          if eachEle == serviceKey:
            serviceValue += 1
        # IF No Quantity For Service
        if serviceValue > 0:
          registeredUser.myCartDict[serviceKey] = serviceValue
      # For Each Service
      for serviceName in registeredUser.myCartDict.keys():
        # RESET Cost Of Service
        costOfService = 0
        for eachEle in listOfServices:
          if eachEle.title() == serviceName:
            getPriceOfService = f"<USER_GETPRICEOFSERVICE>{serviceName}".encode()
            costOfService = int(sendRecvDataFromServer(getPriceOfService))
            break
        # GET The Value With Quantity & Discount
        costValue = costOfService * registeredUser.myCartDict[serviceName] * (1 - registeredUser.discounts[serviceName])
        # Set The Cost To The Same Index In myCartCost Dictionary
        registeredUser.myCartCost[list(registeredUser.myCartDict).index(serviceName)] = costValue
    
    # Prints Invoice List
    mybusinessInfo = []
    # First, grab business info
    # <<Sends A Request To Get Business Info From Server>>
    mybusinessInfo = sendRecvDataFromServer("<USER_GETBUSINESSINFO-->".encode())
    # <<Receives Business Info From Server>>
    mybusinessInfo = mybusinessInfo.split(",")
    # Second, GET Invoice Number
    registeredUser.orderNo = mybusinessInfo.pop(-1)
    
    # Third, GET Expiration Dates Of Each Service
    for eachSer in list(registeredUser.discounts.keys()):
      registeredUser.updatedExpirationDates[eachSer] = "-"
    for eachSer in registeredUser.myCartDict:
      # IF Expired Service Or Never Ordered Service Before
      if registeredUser.expirationDates[eachSer] == "(Expired)" or registeredUser.expirationDates[eachSer] == "-":
        registeredUser.expirationDates[eachSer] = date.today()
        newYearNum = registeredUser.expirationDates[eachSer].year + registeredUser.myCartDict[eachSer]
        datePlaceholder = registeredUser.expirationDates[eachSer] - datetime.timedelta(days=1)
        newDayNum = datePlaceholder.day
        newMonthNum = datePlaceholder.month
        newExpirationDate = datetime.datetime.strptime(f"{newYearNum}-{newMonthNum}-{newDayNum}", "%Y-%m-%d").date()
      else:
        newYearNum = registeredUser.expirationDates[eachSer].year + registeredUser.myCartDict[eachSer]
        newExpirationDate = datetime.datetime.strptime(f"{newYearNum}-{registeredUser.expirationDates[eachSer].month}-{registeredUser.expirationDates[eachSer].day}", "%Y-%m-%d").date()
      # Add The New Dates
      # newExpirationDateArr.append(newExpirationDate)
      registeredUser.updatedExpirationDates[eachSer] = newExpirationDate
      registeredUser.subscriptions[eachSer] += registeredUser.myCartDict[eachSer]
    
    # Checks If There Are Previous Expirations For The Other Unordered Services
    for eachSer in list(registeredUser.updatedExpirationDates.keys()):
      if registeredUser.updatedExpirationDates[eachSer] == "-":
        if registeredUser.expirationDates[eachSer] != "-":
          registeredUser.updatedExpirationDates[eachSer] = registeredUser.expirationDates[eachSer]
    
    # Fourth, GET Current Day
    currentDate = date.today().strftime("%Y-%m-%d")
    
    # Start Printing Invoice
    print("="*100)
    print("-"*80)
    print(f"Business Name:\t\t{mybusinessInfo[0]}")
    print(f"Business Location:\t{mybusinessInfo[1]}")
    print(f"Invoice Number:\t\t{registeredUser.orderNo}")
    print(f"User:\t\t\t{registeredUser.userName}")
    print(f"Date:\t\t\t{currentDate}")
    print("-"*80)
    print(f"Service Name:\t\t\tQuantity:\tCost:\t\tExpiration Date:")
    for num,eachSer in enumerate(registeredUser.myCartDict):
      print(f"{eachSer:16}\t\t{registeredUser.myCartDict[eachSer]}\t\t{registeredUser.myCartCost[num]:.2f}\t\t{registeredUser.updatedExpirationDates[eachSer]}")
    total = 0
    for num in registeredUser.myCartCost:
      total += num
    print("-"*80)
    total *= 1.07
    print(f"Total Cost: ${total:.2f}")
    print("*Inclusive Of GST")
    print("="*100)
    
    while True:
      # Double Confirm
      doubleConfirm = input("Confirm Order? (Y/N):").capitalize()
      if doubleConfirm == "Y":
        # <<Send Data To Inform Server About User Object Being Sent>>
        registeredUserString = pickle.dumps(registeredUser)
        sendRecvDataFromServer("<USER_CONFIRMPAYMENT--->".encode(), registeredUserString, 2)
        time.sleep(1)
        print("Order Made. An Invoice Will Be Sent To You Shortly.")
        print(f"Thank You For Shopping With {mybusinessInfo[0]}!")
        # Leaves Program      
        leaveProgram = True
        return leaveProgram
      elif doubleConfirm == "N":
        print("Cancelling...")
        time.sleep(1)
        break
      else:
        print("Please Enter An Appropriate Value!")
  return leaveProgram


#=====================================================#
# Main Menu: Display Current Subscriptions [Option 4] #
#=====================================================#
def displayCurrentSubscriptions(registeredUser):  
  print("="*60)
  print("Showing Current Subscriptions:")
  print("-"*60)
  print("Service Name\t\tStart Date\tEnd Date")
  print("-"*60)
  # Get Start Date Of Service
  startDateOfServs = []
  for eachVal in registeredUser.expirationDates:
    if registeredUser.expirationDates[eachVal] == "(Expired)":
      startDateOfServs.append("(Expired)")
    elif registeredUser.expirationDates[eachVal] == "-":
      startDateOfServs.append("-")
    else:
      # Calculates the Start Date (Accounts For Leap Year)
      newYearNum = registeredUser.expirationDates[eachVal].year - registeredUser.subscriptions[eachVal]
      datePlaceholder = registeredUser.expirationDates[eachVal] + datetime.timedelta(days=1)
      newDayNum = datePlaceholder.day
      newMonthNum = datePlaceholder.month
      startDate = datetime.datetime.strptime(f"{newYearNum}-{newMonthNum}-{newDayNum}", "%Y-%m-%d").date()
      startDateOfServs.append(startDate)
  # Print Each Subscription
  for eachNum, eachVal in enumerate(registeredUser.expirationDates):
    print(f"{eachVal:16}\t{str(startDateOfServs[eachNum]):14}\t{registeredUser.expirationDates[eachVal]}")
  print("-"*60)


#=======================================#
# Main Menu: Change Password [Option 5] #
#=======================================#
def changeUserPassword(registeredUser):
  # GET New Password
  isValidDoublePass = False
  while True:
    newPassword = getPassword()
    doubleConfirmPass = getPassword()
    
    # Check Length Of Each First
    if len(newPassword) == len(doubleConfirmPass):
      # Check Each Character Of Both Strings
      for eachChar in range(len(newPassword)):
        if newPassword[eachChar] == doubleConfirmPass[eachChar]:
          isValidDoublePass = True
        else:
          isValidDoublePass = False
        
        if isValidDoublePass == False:
          break
    
    if isValidDoublePass:
      break
    else:
      # IF Both Passwords Do Not Match
      print("Passwords Do Not Match!")
  
  stringToSendServer = f"<USER_CHANGEPASSWORD--->{newPassword},{registeredUser.userName}"
  dataFromServer = sendRecvDataFromServer(stringToSendServer.encode())
  print(dataFromServer)


#=====================================#
# Main Menu: Delete Account[Option 6] #
#=====================================#
def pendingDeleteAccount(registeredUser, leaveProgram):
  print("\t\t\t:::DELETION OF ACCOUNT:::")
  print("Deletion Of Account Signifies That All Services That Have Been Ordered\nPreviously Will Be Revoked. There Will Be No Refunds For Any Prepaid\nServices.")
  print("\nBy Confirming This, You Are Enabling Us To Delete Your Account Without\nPrior Notice. You Will Be Unable To Use This Account After\nConfirmation. ")
  doubleConfirm = input("\nAre You Sure (Y/N): ").capitalize()
  if doubleConfirm == "Y":
    dataFromServer = sendRecvDataFromServer(f"<USER_DELETEACCOUNT---->{registeredUser.userName}".encode())
    if dataFromServer == "<DELETED_ACCOUNT>":
      print("Request Has Been Sent To Admin. Deletion Of Account Will Occur Within The Next 24 Hours.\n")
      print("Thank You And Have A Nice Day!")
    leaveProgram = True
  else:
    print("Cancelling Deletion...")
  return leaveProgram


#===================================#
# Main Menu: Leaving ESP [Option 7]
#===================================#
def leavingESP(registeredUser, listOfServices):
  if len(registeredUser.myCart) != 0:
    print("There Are Still Item(s) In Cart!")
    saveCart = input("Do You Want To Save? (Y/N): ").strip().capitalize()
    while True:
      if saveCart == "Y":
        # Check If myCartDict == {}, Means Never Viewed Cart Before Proceeding To Payment
        if registeredUser.myCartDict == {}:
          # Determine The Name Of Services & Their Quantity
          for i in range(0,len(listOfServices)):
            serviceKey = listOfServices[i].title()
            serviceValue = 0
            # Check Quantity For Each Different Service
            for eachEle in registeredUser.myCart:
              if eachEle == serviceKey:
                serviceValue += 1
            # IF No Quantity For Service
            if serviceValue > 0:
              registeredUser.myCartDict[serviceKey] = serviceValue
          # For Each Service
          for serviceName in registeredUser.myCartDict.keys():
            # RESET Cost Of Service
            costOfService = 0
            for eachEle in listOfServices:
              if eachEle.title() == serviceName:
                getPriceOfService = f"<USER_GETPRICEOFSERVICE>{serviceName}".encode()
                costOfService = int(sendRecvDataFromServer(getPriceOfService))
                break
            # GET The Value With Quantity & Discount
            costValue = costOfService * registeredUser.myCartDict[serviceName] * (1 - registeredUser.discounts[serviceName])
            # Set The Cost To The Same Index In myCartCost Dictionary
            registeredUser.myCartCost[list(registeredUser.myCartDict).index(serviceName)] = costValue
        
        cartNumber = sendRecvDataFromServer("<USER_SAVECART--------->".encode(), pickle.dumps(registeredUser), 3)
        print(f"Enter '{cartNumber}' To Retrieve This Cart Order Next Time!\n")
        break
      elif saveCart == "N":
        print("Discarding Cart...")
        break
      else:
        saveCart = input("Please Enter A Valid Input (Y/N): ").strip().capitalize()
  print("Thanks For Using Winston's (E)Service Provider!")


# <----------------------------------> #
#                                      #
#              Start Program           #
#                                      #
#                                      #
# <----------------------------------> #
try:
  print("-=============================-")
  print("Starting Up...")
  
  isValidCredential = False
  leaveProgram = False
  while leaveProgram == False:
    #---------------------#
    # 1. Chooses Category #
    #---------------------#
    while isValidCredential == False:      
      while True:
        try:
          categoryOption = input("\nEnter\n1. For Registered User\n2. For New User\n>> ").strip()
          if int(categoryOption) < 1 or int(categoryOption) > 2:
            print("Enter A Valid Numeric Option!")
          else:
            break
        except:
          print("Please Enter A Valid Option!")
      
      #-----------------------------#
      # Category 1: Registered User #
      #-----------------------------#
      if int(categoryOption) == 1:
        userName = input("Enter Username: ").strip().capitalize()
        userPass = getPassword()
        resetPassword = ""
        if userPass == "": # IF Password If Left Empty
          while resetPassword != "Y" and resetPassword != "N":
            resetPassword = input("Do You Want To Reset Password (Y/N): ").strip().capitalize()
        # Adds To categoryOption To Be Seperated Later
        categoryOption += f",{userName},{userPass},{resetPassword}"
      
      #----------------------#
      # Category 2: New User #
      #----------------------#
      else:
        print("Creating New User...")
        userPass = userPass_Second = ""
        regex = r'^([a-zA-Z]*)$' # Only Alphabets In userName
        # Validate Username
        userName = input("Please Enter A Username [Only Alphabets Allowed]: ")
        while not(re.match(regex, userName)) or userName.capitalize() == "User":
          print("Invalid Username.")
          userName = input("Please Enter A Valid Username [Only Alphabets Allowed]: ")
        # Validate Password
        userPass = getPassword()
        userPass_Second = getPassword()
        while userPass != "" and userPass_Second != "" and userPass != userPass_Second:
          print("Passwords Do Not Match!\n")
          userPass = getPassword()
          userPass_Second = getPassword()
        # Adds To categoryOption To Be Seperated Later
        categoryOption += f",{userName},{userPass}"
      
      # <<Sends Data To Server>>
      categoryOption = "<USER_CHOOSE_CATEGORY-->" + categoryOption
      
      # <<Receive Data Back From Server>>
      # For Registered User:
      if int(categoryOption[24]) == 1:
        if resetPassword != "Y" and resetPassword != "N": # Entered Credentials
          dataFromServer, registeredUser = sendRecvDataFromServer(categoryOption.encode(), "", 1, 23)
          if len(dataFromServer) > 0:
            # Checks If Correct Credentials
            if dataFromServer == "<VALIDATED_CREDENTIALS>":
              isValidCredential = True
            else:
              print("Username Or Password Is Incorrect!")
          # If Connection Is Gone
          else:
            print("No Data From Server.")
        else: # Reset Password
          resetPassword_Message = sendRecvDataFromServer(categoryOption.encode())
          if len(resetPassword_Message) > 0:
            if "PASSWORD_RESET" in resetPassword_Message:
              print(f"User {userName} Has Requested For A Password Reset.\nThe Default Password Of 'Password' Will Be Used.\nPlease Wait For 24 Hours.")
            elif "PASSWORD_ALREADYRESET" in resetPassword_Message:
              print(f"User {userName} Has Requested For A Password Reset Before.\nPlease Wait For 24 Hours.")
            elif "PASSWORD_DENYRESET" in resetPassword_Message:
              print(f"User {userName} Denied To Reset Password.")
          else:
            print("Connection has dropped.")
      # For New Users
      else:
        dataFromServer, registeredUser = sendRecvDataFromServer(categoryOption.encode(), "", 1, 16)
        if len(dataFromServer) > 0:
          # Check If Validated Username + Password
          if not("TAKEN") in dataFromServer:
            isValidCredential = True
          else:
            print("Please Enter A Username That Has Not Been Taken.", end="\n\n")
        else:
          print("Connection has dropped.")
      
      # Check If Valid Credentials, Receive User Info From Server
      if isValidCredential:
        registeredUser = pickle.loads(registeredUser)
    
    #--------------#
    # 2. Main Menu #
    #--------------#
    # User Is Logged In
    # Start Of Registered User Connection
    listOfOptions = ["Search For Service(s)", "View Cart", "Check Out/Payment", "Display Current Subscriptions", "Change Password","Delete Account","Exit ESP"]
    userOption = ""
    listOfServices = list(registeredUser.discounts.keys()) # Get All Names of Services
    
    print("-=============================-\n")
    print("-" * 70)
    print(f"\tWelcome {userName} to Winston's (E)Service Provider:")
    print("-" * 70)
    while leaveProgram == False:
      print("-" * 25)
      print("List of Options:")
      print("-" * 25)
      [print(f"{num}. {option}") for num,option in enumerate(listOfOptions, 1)]
      
      # Validate Option First
      while True:
        try:
          userOption = int(input("\nPlease Choose An Option: ").strip())
          if userOption < 1 or userOption > 7:
            print("Please Enter A Valid Number!")
          else:
            break
        except ValueError:
          print("Please Enter An Integer!")
      
      # Main Menu Option 1: Search Service
      if userOption == 1:
        leaveProgram = client_SearchService(registeredUser, listOfServices, leaveProgram)   
      elif userOption == 2:
        leaveProgram = client_ViewCart(registeredUser, listOfServices, leaveProgram)
      elif userOption == 3:
        leaveProgram = orderPayment(registeredUser, listOfServices, leaveProgram)
      elif userOption == 4:
        displayCurrentSubscriptions(registeredUser)
      elif userOption == 5:
        changeUserPassword(registeredUser)
      elif userOption == 6:
        leaveProgram = pendingDeleteAccount(registeredUser, leaveProgram)
      elif userOption == 7:
        leavingESP(registeredUser, listOfServices)
        leaveProgram = True
except WindowsError:
  print("The ESP Server May Be Down For Maintenance. Sorry For The Inconvinence!")
  print("-=====================================================================-")