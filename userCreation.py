'''
Name:               Seow Wee Hau Winston
Name Of File:       usersCreation.py

Input-Output Files: None - Makes Request To Server

#-----------------------------------------------------------#
This file is made to CREATE A USER OBJECT for any user that
logs in. This ensures that there are attributes for each
user.
#-----------------------------------------------------------#
'''
import time
import datetime
from datetime import date

class User:
  def __init__(self, userName, listOfServices):
    # Discounts and Subscriptions start off as empty dictionaries.
    self.userName = userName
    self.discounts = {}
    self.subscriptions = {}
    self.expirationDates = {}                         # Old expiration dates taken from subscriptions.txt
    self.updatedExpirationDates = {}                  # New expiration dates tabulated for the new services in cart
    self.myCartDict = {}                              # Tabulated cart
    self.myCart = []                                  # Items in cart, not tabulated
    self.myCartCost = [0] * int(len(listOfServices)/2)# Cost of each Item in cart
    self.cartOrderNo = ''                             # Inside Cart Order No
    self.newOrderNo = ''                              # New Order
  
  #--------------------------------------------#
  # Grab Discount/Subscription Of Current User #
  #--------------------------------------------#
  def getDiscountsOrSub(self, fileName):
    keyArr = []
    
    # Open File To Grab Contents
    with open(fileName, 'r') as readableFile:
      readableFile = readableFile.readlines()
      
    for num,eachLine in enumerate(readableFile):
      # Removes All "\n" From Each Line
      readableFile[num] = eachLine.replace("\n","")
      # Grabs The Keys And Removes "# " From Each Key
      if "#" in eachLine and not(":" in eachLine):
        keyArr.append(eachLine.replace("# ","").replace("\n",""))
    
    # Locate The Discounts/Subscriptions And Append To Dictionary
    userNum = 1
    for num,eachLine in enumerate(readableFile):
      if not("#" in eachLine) and "User" in eachLine:
        if f"User {userNum}: {self.userName}" in eachLine:
          startValue = num + 1
          if "discounts.txt" in fileName:
            for counter in range(len(keyArr)):
              dict_value = float(readableFile[startValue])
              dict_key = keyArr[counter]
              self.discounts[dict_key] = dict_value
              startValue += 1
          elif "subscriptions.txt" in fileName:
            subscriptionsKey = expirationDateKey = 0
            # Bring Counter Between (0 to No of ExpirationsDates + Subscriptions)
            for counter in range(0,len(keyArr)*2):
              if counter % 2 == 0:
                dict_value = readableFile[startValue]
                dict_key = keyArr[expirationDateKey]
                expirationDateKey += 1
                if dict_value == "-":
                  self.expirationDates[dict_key] = dict_value
                else:
                  self.expirationDates[dict_key] = datetime.datetime.strptime(dict_value, "%Y-%m-%d").date()
              else:
                dict_value = int(readableFile[startValue])
                dict_key = keyArr[subscriptionsKey]
                self.subscriptions[dict_key] = dict_value
                subscriptionsKey += 1
              startValue += 1
        userNum += 1
  
    # Check The Expiration Date If Service Is Expired
    if "subscriptions.txt" in fileName:
      currentDate = date.today()
      # currentDate = datetime.datetime.strptime(str(date.today()), "%Y-%m-%d").date()
      for eachKey in self.expirationDates:
        if self.expirationDates[eachKey] != "-" and self.expirationDates[eachKey] < currentDate:
          self.expirationDates[eachKey] = "(Expired)"
          self.subscriptions[eachKey] = 0

  # Note: In this function, self.myCart holds all of the added services chosen by user.
  #----------------------#
  # Add Services To Cart #
  #----------------------#
  def addingServices(self, stopAddingToCart, availableServices):
    while True:
      print("="*61)
      print("List Of Service(s) Available: ")
      print("-"*35)
      [print(f"\t{num}. {service}") for num,service in enumerate(availableServices, 1)]
      print("-"*35)
      cartValue = input("Enter The Number Of The Service or ENTER to stop: ")
      # Check If Stop Adding Services
      if cartValue == '':
        print("Finish Adding Services...")
        time.sleep(1)
        stopAddingToCart = True
        break
      # Check If Valid Service To Add
      elif cartValue.isnumeric() == True:
        itemValue = int(cartValue) - 1
        if itemValue < len(availableServices):
          self.myCart.append(availableServices[itemValue])
          print("-"*35)
          print("Added Services:")
          [print(f"\t{num}. {service}") for num,service in enumerate(self.myCart, 1)]
          print("="*61, end="\n\n")
          time.sleep(1)
        else:
          print(f"There are No Services With A Value Of {cartValue}.")
      # No Service At That String
      else:
        print("Please Enter A Number For A Service!")
    return stopAddingToCart
