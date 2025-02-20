from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from datetime import datetime
from datetime import timedelta
from django.utils import timezone
from .serializers import MembersSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Members, Chamas, Contributions, Loans
from django.db.models import Sum
import pyrebase
import json
from django.views.decorators.csrf import csrf_exempt
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

#start of contributions api
@api_view(['GET']) 
def contributions(request, email, amount):
    try:
        member = Members.objects.get(email=email)
        contribution = Contributions(member=member, amount=amount)
        contribution.save()
        return Response({"message":f"Contribution of Ksh.{amount} was successful"})
    except Members.DoesNotExist:
        return Response({"message":"Invalid email address"})

#end of contributions api

#start of loans api

#function to calculate amount of loan allowed
from decimal import Decimal
def check_loan(email):
    member = Members.objects.get(email=email)
    total_amount = Loans.objects.filter(member=member).aggregate(Sum('amount'))['amount__sum'] or 0
    loan = 0
    max_amount = 10000
    if total_amount > max_amount:
        return loan
        
    elif total_amount < max_amount:
        loan = total_amount - (Decimal('0.5') * total_amount)
        return loan

    elif total_amount == 0:
        loan = 10000
        return max_amount
#end of calculate function

@api_view(['GET'])
def loans(request, email, amount, loan_type):
    try:
        member = Members.objects.get(email=email)
        loan_deadline=timezone.now() + timedelta(days=30)
        check = check_loan(email)
        if check > 0:
            loan = Loans(member=member, amount=amount, loan_type=loan_type, loan_deadline=loan_deadline)
            loan.save()
            return Response({"message":f"Loan of Ksh.{amount} of type {loan_type} was successful"})
        else:
            return Response({"message":f"Loan of Ksh.{amount} of type {loan_type} exceeds the maximum loan limit"})
        
    except Members.DoesNotExist:
        return Response({"message":"Invalid email address"})
#end of loans api

@api_view(['GET'])
def loan_allowed(request, email):
    max_loan = check_loan(email)
    return Response({"max_loan":f"Ksh.{max_loan}"})

#start of signin api
def postsignIn(request, email, password):
    try:
        user = authe.sign_in_with_email_and_password(email,password)
    except:
        message = "Invalid Credentials!! Please Check your data"
        return JsonResponse({"message": message})
    session_id = user['idToken']
    request.session['uid'] = str(session_id)
    return JsonResponse({"message": "Successfully logged in"})
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
def postsignUp(request):
    try:
        
        if request.method == 'POST':
            check_member = Members.objects.filter(email=email).values()
            if check_member:
                return JsonResponse({"message":"Email already exists"})
            else:
                data = json.loads(request.body)  # Convert request body to JSON
                chama = data.get("chama")  # Get Chama name
                name = data.get("name")
                email = data.get("email")
                phone_number = data.get("phonenumber")
                password = data.get("password")
                user = authe.create_user_with_email_and_password(email, password)
                uid = user['localId']
                idtoken = request.session['uid']
                print(uid)
                chama = Chamas.objects.get(name=chama)
                member = Members(chama=chama, name=name, email=email, phone_number=phone_number, password=uid)
                member.save()
                return JsonResponse({"message":"Successfully registered"})
        else:
            return JsonResponse({"message":"Invalid request"})

    except:
        return JsonResponse({"message":"Registration failed"})
    return JsonResponse({"message":"Registration successful"})
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

