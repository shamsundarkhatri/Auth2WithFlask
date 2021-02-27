from flask import Flask
from flask import request

app = Flask(__name__)

"""
Charge a credit card
"""
import imp
import os
import sys

from authorizenet import apicontractsv1
from authorizenet.apicontrollers import createTransactionController
def ProcessPayment(CreditCardNumber,CardHolder,ExpirationDate,SecurityCode,amount):
    """
    Charge a credit card
    """

    # Create a merchantAuthenticationType object with authentication details
    # retrieved from the constants file
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name ="6xp8vAU4G"
    merchantAuth.transactionKey ="2U2737pEehxk59BA"

    # Create the payment data for a credit card
    creditCard = apicontractsv1.creditCardType()
    creditCard.cardNumber = CreditCardNumber
    creditCard.expirationDate = ExpirationDate
    creditCard.cardCode = SecurityCode

    # Add the payment data to a paymentType object
    payment = apicontractsv1.paymentType()
    payment.creditCard = creditCard

    # Create order information
    order = apicontractsv1.orderType()
    order.invoiceNumber = "10101"
    order.description = "Golf Shirts"

    # Set the customer's Bill To address
    customerAddress = apicontractsv1.customerAddressType()
    CardHolder=CardHolder.split(" ")
    customerAddress.firstName = CardHolder[0]
    customerAddress.lastName = CardHolder[-1]
    customerAddress.company = "Souveniropolis"
    customerAddress.address = "14 Main Street"
    customerAddress.city = "Pecan Springs"
    customerAddress.state = "TX"
    customerAddress.zip = "44628"
    customerAddress.country = "USA"
 # Set the customer's identifying information
    customerData = apicontractsv1.customerDataType()
    customerData.type = "individual"
    customerData.id = "99999456654"
    customerData.email = "EllenJohnson@example.com"

    # Add values for transaction settings
    duplicateWindowSetting = apicontractsv1.settingType()
    duplicateWindowSetting.settingName = "duplicateWindow"
    duplicateWindowSetting.settingValue = "600"
    settings = apicontractsv1.ArrayOfSetting()
    settings.setting.append(duplicateWindowSetting)

    # setup individual line items
    line_item_1 = apicontractsv1.lineItemType()
    line_item_1.itemId = "12345"
    line_item_1.name = "first"
    line_item_1.description = "Here's the first line item"
    line_item_1.quantity = "2"
    line_item_1.unitPrice = "12.95"
    line_item_2 = apicontractsv1.lineItemType()
    line_item_2.itemId = "67890"
    line_item_2.name = "second"
    line_item_2.description = "Here's the second line item"
    line_item_2.quantity = "3"
    line_item_2.unitPrice = "7.95"

    # build the array of line items
    line_items = apicontractsv1.ArrayOfLineItem()
    line_items.lineItem.append(line_item_1)
    line_items.lineItem.append(line_item_2)

    # Create a transactionRequestType object and add the previous objects to it.
    transactionrequest = apicontractsv1.transactionRequestType()
    transactionrequest.transactionType = "authCaptureTransaction"
    transactionrequest.amount = amount
    transactionrequest.payment = payment
    transactionrequest.order = order
    transactionrequest.billTo = customerAddress
    transactionrequest.customer = customerData
    transactionrequest.transactionSettings = settings
    transactionrequest.lineItems = line_items

    # Assemble the complete transaction request
    createtransactionrequest = apicontractsv1.createTransactionRequest()
    createtransactionrequest.merchantAuthentication = merchantAuth
    createtransactionrequest.refId = "MerchantID-0001"
    createtransactionrequest.transactionRequest = transactionrequest
    # Create the controller
    createtransactioncontroller = createTransactionController(
        createtransactionrequest)
    createtransactioncontroller.execute()

    response = createtransactioncontroller.getresponse()
    if response is not None:
        # Check to see if the API request was successfully received and acted upon
        if response.messages.resultCode == "Ok":
            # Since the API request was successful, look for a transaction response
            # and parse it to display the results of authorizing the card
            if hasattr(response.transactionResponse, 'messages') is True:
                print(
                    'Successfully created transaction with Transaction ID: %s'
                    % response.transactionResponse.transId)
                print('Transaction Response Code: %s' %
                      response.transactionResponse.responseCode)
                print('Message Code: %s' %
                      response.transactionResponse.messages.message[0].code)
                print('Description: %s' % response.transactionResponse.
                      messages.message[0].description)
            else:
                print('Failed Transaction.')
                if hasattr(response.transactionResponse, 'errors') is True:
                    print('Error Code:  %s' % str(response.transactionResponse.
                                                  errors.error[0].errorCode))
                    print(
                        'Error message: %s' %
                        response.transactionResponse.errors.error[0].errorText)
        # Or, print errors if the API request wasn't successful
        else:
            return "Transcation failed. Please enter validate data"


    else:
        print('Null Response.')
        return "Transcation failed. Please enter validate data"
    return 1

@app.route('/', methods = ['POST'])
def Process():
    try:
        if request.method == 'POST':
            try:
                CreditCardNumber=request.form['CreditCardNumber']
                CardHolder=request.form['CardHolder']
                ExpirationDate=request.form['ExpirationDate']
                SecurityCode=request.form['SecurityCode']
                Amount=int(request.form['Amount'])
            except:
                return "The request is invalid: 400 bad request"
            try:
                if Amount>=0 and  Amount<=20:
                    Payment_Response=ProcessPayment(CreditCardNumber,CardHolder,ExpirationDate,SecurityCode,Amount)
                elif Amount>20 and Amount<=500:
                    Payment_Response=ProcessPayment(CreditCardNumber,CardHolder,ExpirationDate,SecurityCode,Amount)
                    if Payment_Response!=1:
                        Payment_Response=ProcessPayment(CreditCardNumber,CardHolder,ExpirationDate,SecurityCode,Amount)
                else:
                   Payment_Response= ProcessPayment(CreditCardNumber,CardHolder,ExpirationDate,SecurityCode,Amount)
                   if Payment_Response!=1:
                       count=1  # count 1 beacuase we have already tried once above.
                       while Payment_Response!=1 and count<=3:
                           Payment_Response=ProcessPayment(CreditCardNumber,CardHolder,ExpirationDate,SecurityCode,Amount)
                           count=count+1
            except Exception as e:
                return e
            if Payment_Response!=1:
                return Payment_Response
            return "Payment is processed: 200 OK"
    except:
        return "Any error: 500 internal server error"

if __name__ == "__main__":
    app.run(debug=True)
