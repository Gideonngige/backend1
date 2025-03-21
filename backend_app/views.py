from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
# from datetime import datetime
from datetime import timedelta
from django.utils import timezone
from .serializers import MembersSerializer, ChamasSerializer, LoansSerializer, NotificationsSerializer, TransactionsSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Members, Chamas, Contributions, Loans, Notifications, Transactions, Investment, profit_distribution, investment_contribution, Expenses
from django.db.models import Sum
import pyrebase
import json
from django.views.decorators.csrf import csrf_exempt
from django_daraja.mpesa.core import MpesaClient
from django.core.mail import send_mail
from django.conf import settings
import requests
from requests.auth import HTTPBasicAuth
import datetime
import base64
# import pyrebase4 as pyrebase

# Create your views here.
config = {
    "apiKey": "AIzaSyBYX6dcWok3ldsw4gFXHEjyKbVs6tONxKc",
    "authDomain": "chamavault-d1d35.firebaseapp.com",
    "databaseURL": "https://chamavault-d1d35-default-rtdb.firebaseio.com/",
    "projectId": "chamavault-d1d35",
    "storageBucket": "chamavault-d1d35.firebasestorage.app",
    "messagingSenderId": "739112708717",
    "appId": "1:739112708717:web:481c8338f8b5fdfb192d64",
    "measurementId": "G-47P7H86QBS"
}
firebase = pyrebase.initialize_app(config)
authe = firebase.auth() 
database = firebase.database()


def index(request):
    from datetime import datetime
    now = datetime.now()
    html = f''' 
    <html>
    <body>
    <h1>Welcome to Chamavault API!</h1>
    <p>The current time is { now}.</p>
    </body>
    </html>
    '''
    return HttpResponse(html)

#start of get members api
@api_view(['GET','POST','DELETE'])
def members(request, email, password):
    if request.method == 'GET':
        # check_password = Members.objects.filter(password=password).values()
        try:
            user = authe.sign_in_with_email_and_password(email,password)
            if user:
                members = Members.objects.all()
                serializer = MembersSerializer(members, many=True)
                return Response(serializer.data)
            else:
                return Response({"message":"Please signin"})
        except:
            return Response({"message":"Invalid password"})
    else:
        return Response({"message":"Invalid access"})
#end of get members api  

#get member api
@api_view(['GET'])
def getMember(request, email):
    try:
        member = Members.objects.get(email=email)
        serializer = MembersSerializer(member)
        return JsonResponse(serializer.data)
    except Members.DoesNotExist:
        return JsonResponse({"message":"Invalid email address"})
#end of get member api

#get chama api
@api_view(['GET'])
def getChama(request, email):
    try:
        chama = Members.objects.get(email=email)
        serializer = ChamasSerializer(chama)
        return JsonResponse(serializer.data)
    except Members.DoesNotExist:
        return JsonResponse({"message":"Invalid chama name"})
#end of get chama api

#start of contributions api
# @csrf_exempt
@api_view(['POST']) 
def contributions(request):
    try:
        data = json.loads(request.body) 
        email = data.get('email')
        amount = data.get('amount')
        phonenumber = data.get('phonenumber')
        chama_id = data.get('chama')
        print(chama_id)

        member = Members.objects.get(email=email)
        chama = Chamas.objects.get(name=f"Chama{chama_id}")
        print(chama)
        if member:
            contribution = Contributions(member=member, amount=amount, chama=chama)
            contribution.save()
            transaction = Transactions(member=member, amount=amount, chama=chama, transaction_type="Contribution")
            transaction.save()
            return JsonResponse({"message":f"Contribution of Ksh.{amount} to chama{chama_id} was successful","status":200})
        else:
            return JsonResponse({"message":"Please signin"})

    except Members.DoesNotExist:
        return Response({"message":"Invalid email address"})

#end of contributions api

#start of get transactions api
def transactions(request, transaction_type, email):
    member = Members.objects.get(email=email)
    try:
        if not member:
            return JsonResponse({"message":"Please signin"})
        else:
            transactions = Transactions.objects.filter(member=member, transaction_type=transaction_type).order_by('-transaction_date')
            serializer = TransactionsSerializer(transactions, many=True)
            return JsonResponse(serializer.data, safe=False)
    except Members.DoesNotExist:
        return JsonResponse({"message":"Invalid email address"})

#end of get transactions api

#start of loans api

#function to calculate amount of loan allowed
from decimal import Decimal
from django.db.models import Sum

def check_loan(email):
    try:
        member = Members.objects.get(email=email)
    except Members.DoesNotExist:
        return "Member not found"

    total_amount = Loans.objects.filter(name=member).aggregate(Sum('amount'))['amount__sum'] or 0
    max_amount = 10000  # Maximum loan amount
    
    if total_amount == 0:
        return max_amount  # If no loan exists, they can get the full amount
    
    elif total_amount > max_amount:
        return 500  # Fixed loan amount if they exceed max

    else:
        return float(total_amount) * 0.5  # Half of their current loan balance

#end of calculate function

@api_view(['GET'])
def loans(request, email, chama_id, amount, loan_type, period):
    try:
        member = Members.objects.get(email=email)
        chama = Chamas.objects.get(name=f"Chama{chama_id}")
        print(member)
        print(chama)
        loan_deadline=timezone.now() + timedelta(days=period)
        print(loan_deadline)
        check = check_loan(email)
        print(check)
        if check == 500:
            loan = Loans(name=member, chama=chama, amount=check, loan_type=loan_type, loan_deadline=loan_deadline)
            loan.save()
            transaction = Transactions(member=member, amount=amount, chama=chama, transaction_type="Loan")
            transaction.save()
            return Response({"message":f"Loan of Ksh.{amount} of type {loan_type} was successful","status":200})

        elif check > 0:
            loan = Loans(name=member,chama=chama, amount=amount, loan_type=loan_type, loan_deadline=loan_deadline)
            loan.save()
            transaction = Transactions(member=member, amount=amount, chama=chama, transaction_type="Loan")
            transaction.save()
            return Response({"message":f"Loan of Ksh.{amount} of type {loan_type} was successful","status":200})
        else:
            return Response({"message":f"Loan of Ksh.{amount} of type {loan_type} exceeds the maximum loan limit"})
        
    except Members.DoesNotExist:
        return Response({"message":"Invalid email address"})

#end of loans api

@api_view(['GET'])
def loan_allowed(request, email):
    max_loan = check_loan(email)
    return Response({"max_loan":f"Ksh.{max_loan}"})

#start of get loans api
def getLoans(request, chamaname, email):
    try:
        member = Members.objects.get(email=email)
        if member:
            chama_name = Chamas.objects.get(name=chamaname)
            total_loan = Loans.objects.filter(name=member,chama=chama_name).aggregate(total=Sum('amount'))['total'] or 0.00
            loan_date = list(Loans.objects.filter(name=member, chama=chama_name).values('loan_date'))
            return JsonResponse({"total_loan": total_loan,"loan_date":loan_date, "interest":9.5}, safe=False)

        else:
            return JsonResponse({"message":"No loans found"})
    except Members.DoesNotExist:
        return JsonResponse({"message":"Invalid email address"})
#end of getLoans api 

#start of get all loans
@api_view(['GET'])
def getAllLoans(request):
    try:
        loans = Loans.objects.all()
        serializer = LoansSerializer(loans, many=True)
        return JsonResponse(serializer.data, safe=False)
    except Loans.DoesNotExist:
        return JsonResponse({"message":"No loans found"})
    except Exception as e:
        return JsonResponse({"error":str(e)})
#end of get all loan

#start of confirm loan api
def confirm_loan(request, loanee_id, approver_email):
    try:
        # Get the loanee
        loanee = Loans.objects.filter(name=loanee_id).first()
        if not loanee:
            return JsonResponse({"message": "Loanee not found"}, status=404)

        # Get the approver
        approver = Members.objects.filter(email=approver_email).first()
        if not approver:
            return JsonResponse({"message": "Invalid approver email"}, status=400)

        # Approve the loan
        loanee.approved_by = approver  # Assuming approved_by is a ForeignKey to Members
        loanee.save()

        new_loanee_id = Members.objects.get(member_id=loanee_id)

        # Create a notification
        notification = Notifications(
            member_id=new_loanee_id,  
            notification_type="alert",
            notification=f"Loan of Ksh.{loanee.amount} was approved by {approver_email}"
        )
        notification.save()

        return JsonResponse({"message": f"You have successfully approved KES.{loanee.amount}"})

    except Exception as e:
        return JsonResponse({"message": f"An error occurred: {str(e)}"}, status=500)
    
#end of confirm loan api

#start of get notifications api 
def get_notifications(request, email):
    try:
        member_id = Members.objects.filter(email=email).first()
        notifications = Notifications.objects.filter(member_id=member_id).order_by('notification_date')
        serializer = NotificationsSerializer(notifications, many=True)
        return JsonResponse(serializer.data, safe=False)
    except Notifications.DoesNotExist:
        return JsonResponse({"message":"No notifications found"})
    except Exception as e:
        return JsonResponse({"error":str(e)})


#end get notifications api


#start of getSavings api
def getContributions(request, chamaname, email):
    try:
        member = Members.objects.get(email=email)

        if member:
            chama_name = Chamas.objects.get(name=chamaname)
            total_contributions = Contributions.objects.filter(member=member, chama=chama_name).aggregate(total=Sum('amount'))['total'] or 0.00
            penalty = Contributions.objects.filter(member=member, chama=chama_name).aggregate(Sum('penality'))['penality__sum'] or 0.00
            saving_date = list(Contributions.objects.filter(member=member, chama=chama_name).values('contribution_date'))
            return JsonResponse({"total_contributions": total_contributions,"saving_date":saving_date, "interest":9.5, "penalty":penalty}, safe=False)

        else:
            return JsonResponse({"message":"No Contributions found"})
    except Members.DoesNotExist:
        return JsonResponse({"message":"Invalid email address"})
#end of getSavings api 

#start of investment api 
@api_view(['POST'])
def investment(request):
    try:
        data = json.loads(request.body) 
        member_id = data.get('member_id')
        chama = data.get('chama')
        contribution_amount = data.get('contribution_amount')
        investment_type = data.get('investment_type')
       

        member = Members.objects.get(member_id=member_id)
        investment_id = Investment.objects.get(investment_type=investment_type)
        chama = Chamas.objects.get(name=f"Chama{chama_id}")
        if member:
            contribution = investment_contribution(investment_id=investment_id, member_id=member, contribution_amount=contribution_amount)
            contribution.save()
            transaction = Transactions(member=member, amount=contribution_amount, chama=chama, transaction_type="Contribution")
            transaction.save()
            return JsonResponse({"message":f"Investment of Ksh.{contribution_amount} was successful","status":200})
        else:
            return JsonResponse({"message":"Please signin"})

    except Members.DoesNotExist:
        return Response({"message":"Invalid email address"})
#end of investment api

#start of get investmet 
def getInvestment(request, email):
    try:
        # Get the member based on email
        member = Members.objects.get(email=email)
        
        # Fetch the member's investment contributions and profit distributions
        investment_contri = investment_contribution.objects.filter(member_id=member)
        profit_distri = profit_distribution.objects.filter(member_id=member)

        # Initialize variables for total amounts (assuming you want to sum these up)
        total_investment_amount = 0
        total_profit_amount = 0
        investment_type = None  # Initialize investment_type as None

        # Loop through the investment contributions and get details
        for contribution in investment_contri:
            total_investment_amount += contribution.contribution_amount  # Sum up the contribution amount
            investment_type = contribution.investment_id.investment_type  # Assuming each contribution relates to an investment type

        # Loop through the profit distributions and get profit details
        for profit in profit_distri:
            total_profit_amount += profit.profit_amount  # Sum up the profit amounts

        # If no investments are found for the member, handle that case
        if total_investment_amount == 0 and total_profit_amount == 0:
            return JsonResponse({"message": "No investments or profits found for this member"})

        # Return the response with investment and profit data
        return JsonResponse({
            "investment_amount": total_investment_amount,
            "investment_type": investment_type,
            "profit_amount": total_profit_amount
        })

    except Members.DoesNotExist:
        return JsonResponse({"message": "Member with this email does not exist"})
    except Exception as e:
        return JsonResponse({"error": str(e)})
#end of get investment


#start of signin api
def postsignIn(request, email, password):
    try:
        user = authe.sign_in_with_email_and_password(email,password)
        if Members.objects.filter(email=email).exists() and user:
            session_id = user['idToken']
            request.session['uid'] = str(session_id)
            return JsonResponse({"message": "Successfully logged in"})
        elif not Members.objects.filter(email=email).exists():
            return JsonResponse({"message": "No user found with this email,please register"})
        elif not user:
            return JsonResponse({"message": "Invalid email"})
        else:
            return JsonResponse({"message": "please register"})
    except:
        message = "Invalid Credentials!! Please Check your data"
        return JsonResponse({"message": message})
    
    
#end of signin api

#start of logout api
def logout(request):
    try:
        del request.session['uid']
    except:
        pass 
    return JsonResponse({"message": "Successfully logged out"})
#end of logout api

#start of signUp api
@csrf_exempt
@api_view(['POST'])
def postsignUp(request):
    try:
        data = json.loads(request.body)  # Convert request body to JSON
        
        # Extract data
        email = data.get("email")  # Define email first
        chama_name = data.get("chama")
        name = data.get("name")
        phone_number = data.get("phone_number")
        password = data.get("password")

        # Check if email already exists
        if Members.objects.filter(email=email).exists():
            return JsonResponse({"message": "Email already exists"}, status=400)

        # Create user
        user = authe.create_user_with_email_and_password(email, password)
        uid = user['localId']
        
        # Check if chama exists
        try:
            chama = Chamas.objects.get(name=chama_name)
        except Chamas.DoesNotExist:
            return JsonResponse({"message": "Chama not found"}, status=400)

        # Save member
        member = Members(chama=chama, name=name, email=email, phone_number=phone_number, password=uid)
        member.save()

        return JsonResponse({"message": "Successfully registered"}, status=201)

    except Exception as e:
        print("Error:", str(e))  # Log error for debugging
        return JsonResponse({"message": "Registration failed", "error": str(e)}, status=500)
#end of signUp api

#end of reset api
def postReset(request, email):
    try:
        authe.send_password_reset_email(email)
        message = "A email to reset password is successfully sent"
        return JsonResponse({"message": message})
    except:
        message = "Something went wrong, Please check the email, provided is registered or not"
        return JsonResponse({"message": message})
#start of reset api

#start of create chama api
@csrf_exempt
@api_view(['POST'])
def createchama(request):
    try:
        data = json.loads(request.body)
        chama = data.get('chama')
        description = data.get('description')
        created_by = data.get('created_by')
        if Chamas.objects.filter(name=chama).exists():
            return JsonResponse({"message": "Chama already exists"}, status=400)
        else:
            amount = 0
            chama_instance = Chamas(name=chama, amount=amount, created_by=created_by, description=description)
            chama_instance.save()
            return JsonResponse({"message": "Chama created successfully"}, status=201)
    except:
        return JsonResponse({"message": "Chama creation failed"}, status=500)
#end of create chama api


#start of send email api
def sendEmail(request, email_to, applink):
    subject = 'Invitation to ChamaVault'
    r_email = email_to
    message = f'Hi there, \n\n I would like to invite you to check out this amazing app :{applink}n\nCheers!'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [r_email]
    send_mail( subject, message, email_from, recipient_list)
    return JsonResponse({"message": "ok"})

#end of send email api

# start of mpesa api aprt
def get_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    consumer_key = "17tijAWZQBWLRIFFuJrDGBfl1zalwr00g6wEE20cGdeHvw7l"
    consumer_secret = "iX29aYc7ujvLlXssKhvG2ilFzS7Bpoa5dU9SIGoPUDrdkLWwKQD1rUEOhW7BRQ3e"
    response = requests.get(url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    return response.json().get("access_token")


def generate_mpesa_password():
    business_shortcode = "174379" 
    passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"  
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Generate password using base64 encoding
    password = base64.b64encode(f"{business_shortcode}{passkey}{timestamp}".encode()).decode()
    return password, timestamp

def stk_push(request, phone_number, amount):
    access_token = get_access_token()
    password, timestamp = generate_mpesa_password()
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "BusinessShortCode": "174379",
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": "174379",
        "PhoneNumber": phone_number,
        "CallBackURL": "https://backend1-1cc6.onrender.com/",
        "AccountReference": "Chamavault",
        "TransactionDesc": "Payment description"
    }
    response = requests.post(url, json=payload, headers=headers)
    # return HttpResponse(response)
    res_data = response.json()

    if res_data.get("ResponseCode") == "0":
        checkout_request_id = res_data.get("CheckoutRequestID")

        return JsonResponse({"message":"ok"}, status=200)
    else:
        return JsonResponse({"message":"failed"}, status=400)


#end of mpesa api part