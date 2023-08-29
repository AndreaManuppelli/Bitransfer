from django.shortcuts import render
from .models import *
from uuid import uuid4
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.core.cache import cache
from django.contrib.auth import authenticate
from django.conf import settings
import bitcoin
from django.utils import timezone
import requests
import math
from .wallet import Wallet
from .decorators import *
import hashlib
import base58
from urllib.parse import urlparse





#### FUNCTIONS ####


def is_valid_url(url):
    """
    Function to check if url is valid
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def validate_bitcoin_address(address):
    """
    Function to check if bitcoin address is valid
    """

    try:
        # Decode the address
        decoded_address = base58.b58decode_check(address)
        
        # Check if the address length is correct
        if len(decoded_address) != 25:
            return False
        
        # Check the version
        version = decoded_address[0]
        if version not in (0, 5):
            return False

    except ValueError:
        return False

    return True

def get_time_threshold(time):
    return timezone.now() - settings.PAYMENTS_TIME_RANGE


def satoshi_to_bitcoin(satoshi):
    return satoshi / 100000000




def request_still_valid(address):
    """Function to check if payment request is still valid for payments"""
    obj = Payments.objects.filter(address=address).first()
    now = timezone.now()
    difference = now - obj.creation
    # Check and return if are passed x hours
    return settings.PAYMENTS_TIME_RANGE >= difference

def round_up(amount, decimals):
    return math.ceil(amount * 10**decimals) / 10**decimals

def no_notation(num):
    """
    Function to suppress scientific notation
    """
    return f'{num:.8f}'

def usd_to_coins(amount):
    """
    Function to convert usd into crypto coins
    """

    obj = CoinsRate.objects.last()
    return {
        "bitcoin": round_up(amount=(amount / obj.bitcoin), decimals=8),
    }

def btc_to_usd(amount):
    """
    Function to convert btc to usd
    """

    obj = CoinsRate.objects.last()
    return round_up(amount=(amount * obj.bitcoin), decimals=2)

def is_in_coins(coin_name):
    """
    Function to check if specified is
    in coins list in settings
    """
    is_in_list = False
    for i in settings.COINS_LIST:
        if i["name"] == coin_name:
            is_in_list = True
    return is_in_list


def update_coins_rate():
    """
    Function to get coins prices and fees and save it into DB
    """
    response = requests.get(url="https://api.blockchain.info/mempool/fees")
    data = response.json()
    btc_fee_per_byte = data["regular"]
    response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd')
    data = response.json()
    bitcoin = data["bitcoin"]["usd"]
    response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=litecoin&vs_currencies=usd')
    data = response.json()
    litecoin = data["litecoin"]["usd"]
    response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=dogecoin&vs_currencies=usd')
    data = response.json()
    dogecoin = data["dogecoin"]["usd"]
    response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=dash&vs_currencies=usd')
    data = response.json()
    dash = data["dash"]["usd"]
    
    
    date = timezone.now()
    instance = CoinsRate(bitcoin=bitcoin, dogecoin=dogecoin,
                         litecoin=litecoin, dash=dash, date=date,
                         fee_btc_per_byte=btc_fee_per_byte)
    instance.save()
    # Delete all old records
    CoinsRate.objects.exclude(date=date).delete()
    return True


def user_exists(username):
    try:
        CustomUser.objects.get(username=username)
        return True
    except CustomUser.DoesNotExist:
        return False 

def is_valid_bitcoin_address(address):
    try:
        bitcoin.base58.decode(address)
        return True
    except ValueError:
        return False


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0] 
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def new_payment(username, amount, label, coin, signal_url, redirect_url): 
    # Create wallet btc instance
    walletBTC = Wallet.Btc(user=settings.BTC_RPC_USER, password=settings.BTC_RPC_PSW, wallet_name=settings.BTC_WALLET_NAME)

    # Get address
    address = walletBTC.get_new_address()

    # Generate random id
    id = uuid4()

    # Crete ORM instance
    instance = Payments(address=address, owner=username, creation=timezone.now(),
                         id=id, coin=coin, incorrect_payment=False,
                         amount=amount, paid=False, withdrawn=False, paid_not_confirmed=False,
                         label=label, paid_not_confirmed_incorrect=False, recived=False,
                         signal_url=signal_url, redirect_url=redirect_url, recived_unconfirmed=0,
                         tx_confirmations=0)
    # Save instance to db
    instance.save()
    return {
        "address": address,
        "id": id
    }

###############







#### VIEWS ####

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
 
    ip = get_client_ip(request)

    # Get login attemps for antispam / bruteforce attacks
    attempts = cache.get(ip, 0)

    # Check if the attempts have exceeded the limit
    if attempts >= settings.MAX_REGISTRATION_ATTEMPTS:
        return Response({"detail": "Too many registration attempts."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

    # Get username and password from request
    username = request.data.get("username")
    password = request.data.get("password")

    # Check if username and password are not empty
    if not username or not password:
        return Response({"detail": "Username and password required."}, status=status.HTTP_400_BAD_REQUEST)
    # Check username length
    if len(username) < 8:
        # Increse login attemps
        attempts += 1
        return Response({"detail": "The username must be at least 14 characters long."}, status=status.HTTP_400_BAD_REQUEST)

    # Check password length for security
    if len(password) < 14:

        # Increse login attemps
        attempts += 1

        return Response({"detail": "The password must be at least 14 characters long."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user already exist
    if user_exists(username=username):

        # Increse login attemps
        attempts += 1

        return Response({"detail": "Username already exist."}, status=status.HTTP_400_BAD_REQUEST)

    # Crete new user in db
    user = CustomUser.objects.create_user(username=username, password=password, btc_balance=0, plan=0, remaining_days_plan=0)

    # Get auth token
    token = Token.objects.create(user=user)

    # Increase registration attemps
    cache.set(ip, attempts, settings.REGISTRATION_TIMEOUT_SECONDS)

    # Return token and message
    return Response({"token": token.key,
                     "detail": "Registered successfully."}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    # Get username and password from request
    username = request.data.get("username")
    password = request.data.get("password")

    # Check if credentials are valid, so let login the user
    user = authenticate(request, username=username, password=password)

    # Check auth status and login
    if user is not None:
        # Get auth token
        token, created = Token.objects.get_or_create(user=user)

        # Return login token
        return Response({'token': token.key, "detail": "Logged."}, status=status.HTTP_202_ACCEPTED)
    else:
        return Response({"detail": "Wrong credentials."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unlog_user(request):
    """
    View function to delete all user's sessions
    """

    # Get user
    User = get_user_model()
    user = User.objects.get(username=request.user.username)

    # Get all sessions
    sessions = Session.objects.filter(expire_date__gte=timezone.now())

    # Look for the user's sessions
    for session in sessions:
        session_data = session.get_decoded()
        if user.id == session_data.get('_auth_user_id'):
            session.delete()  # Delete the session



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@dynamic_ratelimit
def new_payment_view(request):
    """
    Function view to create new payment request.
    """

    # Get username from request
    username = request.user.username
    
    # Get chosen coin from request
    coin = request.data.get("coin")

    # Get chosen label from request
    label_sent = request.data.get("label")

    # Get amount from request
    amount_sent = request.data.get("amount")

    # Get url to ping after confirmed payment from request
    signal_url = request.data.get("signal_url")

    # Get url for redirect after payment in mempool
    redirect_url = request.data.get("redirect_url")

    # Check if redirect url has been entered
    if redirect_url:

        # If url is invalid return error
        if not is_valid_url(redirect_url):
            return Response({"detail": "The redirect url is invalid."}, status=status.HTTP_400_BAD_REQUEST)
        
    # Check if signal url has been entered
    if signal_url:

        # If url is invalid return error
        if not is_valid_url(signal_url):
            return Response({"detail": "The signal url is invalid."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if inputs ("coin", "amount") are compiled
    if coin == None or amount_sent == None:
        return Response({"detail": "Coin and amount are mandatory."}, status=status.HTTP_400_BAD_REQUEST)

    # If spcified coin is not in listed in settings return error
    if not is_in_coins(coin):
        return Response({"detail": f"the coin: {coin} is not in coins list"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if "label" is a string
    if isinstance(label_sent, str):
        label = label_sent
    elif label_sent == None:
        label = ""
    else:
        return Response({"detail": "Label is not a string."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if length exceed and set label
    if len(label) <= 10000:
        label = label
    else:
        return Response({"detail": "Label exceeds the character limit allowed."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Try to convert "amount_sent" in a float else is not a number and return error
    try:
        amount = float(amount_sent)
    except:
        return Response({"detail": "Amount is not a number."}, status=status.HTTP_400_BAD_REQUEST)

    # Double check if "amount_sent" is not a number, in this case return error
    if not isinstance(amount, (int, float)):
        return Response({"detail": "Amount is not a number."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if "amount_sent" exceed maximum allowed, in this case return error
    if amount > settings.MAXIMUM_PAYMENT_IN_USD:
        return Response({"detail": "Label exceeds the character limit allowed."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if "amount_sent" is less than the minimum, in this case return error
    if float(amount_sent) < settings.MINIMUM_PAYMENT_IN_USD - 1:
        return Response({"detail": f"Amount is less than the minimum: ${amount_sent}. Minimum required: ${settings.MINIMUM_PAYMENT_IN_USD}"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get expected amount in $ from request and convert into coin value
    amount = usd_to_coins(amount=amount)[coin]

    # Create new payment request into db and assign returned data to variable
    payment_data = new_payment(username=username, coin=coin, amount=amount, label=label, redirect_url=redirect_url, signal_url=signal_url)

    # Get address from payment data
    address = payment_data["address"]

    # Get id from payment data
    id = payment_data["id"]

    return Response({"id": id,
                     "address": address,
                     "coin": coin,
                     "coins_amount": no_notation(amount),
                     "testnet": settings.TESTNET,
                     "detail": "Payment request created successfully."}, status=status.HTTP_201_CREATED)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment_requests(request):
    """
    View function to get all own payments data
    """

    # Get all own payment requests
    all_user_requests = Payments.objects.filter(owner=request.user.username)

    # Create list to append data
    user_requests_list = []

    # Iterate each result
    for i in all_user_requests:

        # Transform and append to "user_requests_list" each result
        user_requests_list.append(
            {
                "id": i.id,
                "address": i.address,
                "coin": i.coin,
                "amount": i.amount,
                "description": i.label,
                "creation": i.creation,
                "paid": i.paid,
                "withdrawn": i.withdrawn,
                "still_valid": request_still_valid(i.address),
                "paid_not_confirmed": i.paid_not_confirmed,
                "paid_not_confirmed_incorrect": i.paid_not_confirmed,
                "withdrawn": i.withdrawn,
                "incorrect_payment": i.incorrect_payment,
                "amount_recived": i.recived,
                "creation_datetime": i.creation,
                "signal_url": i.signal_url,
                "redirect_url": i.redirect_url,
                "tx_confirmations": i.tx_confirmations
            }
        )
    return Response(user_requests_list, status=status.HTTP_202_ACCEPTED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_active_payment_requests(request):
    """
    View function to get only active own payments data
    """

    time_threshold = timezone.now() - settings.PAYMENTS_TIME_RANGE

    # Get all own active payment requests
    active_user_requests = Payments.objects.filter(creation__gte=time_threshold).filter(owner=request.user.username)

    # Create list to append data
    user_requests_list = []

    # Iterate each result
    for i in active_user_requests:

        # Transform and append to "user_requests_list" each result
        user_requests_list.append(
            {
                "id": i.id,
                "address": i.address,
                "coin": i.coin,
                "amount": i.amount,
                "description": i.label,
                "creation": i.creation,
                "paid": i.paid,
                "withdrawn": i.withdrawn,
                "still_valid": i.address,
                "paid_not_confirmed": i.paid_not_confirmed,
                "paid_not_confirmed_incorrect": i.paid_not_confirmed,
                "withdrawn": i.withdrawn,
                "incorrect_payment": i.incorrect_payment,
                "amount_recived": i.recived,
                "amount_recived_unconfirmed": i.recived_unconfirmed,
                "creation_datetime": i.creation,
                "signal_url": i.signal_url,
                "redirect_url": i.redirect_url,
                "tx_confirmations": i.tx_confirmations
            }
        )
    return Response(user_requests_list, status=status.HTTP_202_ACCEPTED)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_payment_request_by_address_public(request):
    """
    View function to get specific payment
    by address. Return censored data
    """

    # Get address from request
    address = request.data.get("address")

    # Filtered result by address
    payment_request = Payments.objects.filter(address=address)

    # Check if payment exsist
    if payment_request.exists():
        payment_request = payment_request.first()
        return Response({
            "id": payment_request.id,
            "coin": payment_request.coin,
            "address": address,
            "creation_datetime": payment_request.creation,
            "amount": payment_request.amount,
            "paid": payment_request.paid,
            "paid_not_confirmed": payment_request.paid_not_confirmed,
            "paid_not_confirmed_incorrect": payment_request.paid_not_confirmed_incorrect,
            "amount_recived": payment_request.recived,
            "amount_recived_unconfirmed": payment_request.recived_unconfirmed,
            "redirect_url": payment_request.redirect_url,
            "tx_confirmations": payment_request.tx_confirmations,
            "incorrect_payment": payment_request.incorrect_payment
        }, status=status.HTTP_202_ACCEPTED)
    else:
        return Response({"detail": "No payment request match with this address"}, status=status.HTTP_400_BAD_REQUEST)
    



@api_view(['POST'])
@permission_classes([AllowAny])
def get_payment_request_by_id_public(request):
    """
    View function to get specific payment
    by id. Return censored data
    """

    # Get id from request
    id = request.data.get("id")

    # Filtered result by id
    payment_request = Payments.objects.filter(id=id)

    # Check if payment exsist
    if payment_request.exists():
        payment_request = payment_request.first()
        return Response({
            "id": payment_request.id,
            "coin": payment_request.coin,
            "address": payment_request.address,
            "creation_datetime": payment_request.creation,
            "amount": payment_request.amount,
            "paid": payment_request.paid,
            "paid_not_confirmed": payment_request.paid_not_confirmed,
            "paid_not_confirmed_incorrect": payment_request.paid_not_confirmed_incorrect,
            "amount_recived": payment_request.recived,
            "amount_recived_unconfirmed": payment_request.recived_unconfirmed,
            "redirect_url": payment_request.redirect_url,
            "tx_confirmations": payment_request.tx_confirmations,
            "incorrect_payment": payment_request.incorrect_payment
        }, status=status.HTTP_202_ACCEPTED)
    else:
        return Response({"detail": "No payment request match with this id"}, status=status.HTTP_400_BAD_REQUEST)
    




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw_funds(request):
    """
    View to withdraw funds from payment
    requests associated with the user
    """

    # Get username from request
    username = request.user.username

    # Get the address to send the funds to from the request
    address = request.data.get("address")

    # Get chosen coin from request
    coin = request.data.get("coin")

    # Check if selected coin is bitcoin
    if coin == "bitcoin":

        # Check if bitcoin address is valid
        if validate_bitcoin_address(address):

            # Get associated payment request excluding payment requests that have already been withdrawn
            payments_to_be_withdrawn = Payments.objects.filter(owner=username).filter(withdrawn=False).filter(paid=True).filter(coin="bitcoin")
            
            # Mark all payments as withdrawn before withdrawal for safety
            Payments.objects.filter(owner=username).filter(coin="bitcoin").filter(paid=True).update(withdrawn=True)

            # check if the user has withdrawable funds
            if payments_to_be_withdrawn.exists():

                funds_to_withdraw = 0

                # Iterate each payment request and add amount to funds to withdraw
                for i in payments_to_be_withdrawn:
                    funds_to_withdraw += i.recived
                
                # Check that the withdrawable funds are greater than the minimum withdrawable
                if funds_to_withdraw >= usd_to_coins(settings.MINIMUM_WHITDRAW_IN_USD)["bitcoin"]:

                    # Create wallet instance
                    walletBTC = Wallet.Btc(user=settings.BTC_RPC_USER, password=settings.BTC_RPC_PSW, wallet_name=settings.BTC_WALLET_NAME)

                    # Send btc to address
                    walletBTC.send_to_address(amount_btc=funds_to_withdraw, recipient_address=address)

                    return Response({"detail": "funds withdrawn successfully."}, status=status.HTTP_202_ACCEPTED)
                
                else:
                    return Response({"detail": "The withdrawable funds are less than the minimum withdrawable."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"detail": "You have no withdrawable payment requests at the moment."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": f"The address {address} it not a valid bitcoin address."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"detail": f"Not valid selected coin: {coin}."}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_funds(request):
    """
    View to get available withdrawable funds
    """

    # Get username from request
    username = request.user.username

    # Get associated payment request excluding payment requests that have already been withdrawn
    withdrawable_payments = Payments.objects.filter(owner=username).filter(withdrawn=False).filter(paid=True).filter(coin="bitcoin")
    
    # check if the user has withdrawable funds
    if withdrawable_payments.exists():

        btc_funds = 0

        # Iterate each payment request and add amount to funds to withdraw
        for i in withdrawable_payments:
            btc_funds += i.recived

        return Response({"btc_amount": btc_funds,
                         "usd_amount": btc_to_usd(btc_funds)}, status=status.HTTP_202_ACCEPTED)
    else:
        return Response({"btc_amount": 0,
                         "usd_amount": 0}, status=status.HTTP_202_ACCEPTED)




@api_view(['GET'])
@permission_classes([AllowAny])
def available_plans(request):
    return Response(settings.USER_PLANS_LIST, status=status.HTTP_202_ACCEPTED)


@api_view(['GET'])
@permission_classes([AllowAny])
def coins_rate(request):
    return Response({"btc": CoinsRate.objects.all().first().bitcoin}, status=status.HTTP_202_ACCEPTED)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_plan(request):

    # Get username from request
    username = request.user.username

    # Get actual user's plan
    actual_plan_id = request.user.plan

    # Get the plan that the user intends to buy from the request
    chosen_plan_id = int(request.data.get("plan_id"))

    # Get plans available from settings
    plans_available = settings.USER_PLANS_LIST

    # Check if selected plan is in plans available
    if len([d for d in plans_available if d['id'] == chosen_plan_id]) > 0:

        # Filter plans available to get corresponding actual plan data by id
        actual_plan_data = [d for d in plans_available if d['id'] == actual_plan_id][0]

        # Filter plans available to get corresponding chosen plan data by id
        chosen_plan_data = [d for d in plans_available if d['id'] == chosen_plan_id][0]

        # Get time threshold from settings
        time_threshold = timezone.now() - settings.PAYMENTS_TIME_RANGE

    

        # Check if cosen plan is greater than of actual
        if actual_plan_id <= chosen_plan_id:

            active_pending_payments = PurchasedPlans.objects.filter(creation__gte=time_threshold).filter(paid=False).filter(incorrect_payment=False).filter(username_buyer=username)
            # Check if there are already pending payments
            if active_pending_payments.exists():
                return Response({"detail": 'You already have a pending payment, complete the payment if you still have time otherwise wait for the deadline and try again.'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:

                # Create btc wallet instance
                walletBTC = Wallet.Btc(user=settings.BTC_RPC_USER, password=settings.BTC_RPC_PSW, wallet_name=settings.BTC_WALLET_NAME)

                # Generate new address
                address = walletBTC.get_new_address()
                
                # Get amount in BTC
                amount = usd_to_coins(chosen_plan_data["price"])["bitcoin"]
    
                # Create ORM instance
                p = PurchasedPlans(id=uuid4(), username_buyer=username, address=address, creation=timezone.now(),
                                amount=amount, paid=False,
                                plan_id=chosen_plan_id, withdrawn=False, incorrect_payment=False, recived=0)
                
                # Save purchase plan request into db
                p.save()

                return Response({"btc_amount": amount,
                         "address": address,
                         "remaining_time_in_seconds": settings.PAYMENTS_TIME_RANGE}, status=status.HTTP_202_ACCEPTED)
                
        else:
            return Response({"detail": f'The chosen plan is lower than your already active plan. your plan is "{actual_plan_data["name"]}", you chosen "{chosen_plan_data["name"]}"'},
                            status=status.HTTP_400_BAD_REQUEST)
        
    else:
        return Response({"detail": 'The chosen plan not exist'},
                            status=status.HTTP_400_BAD_REQUEST)
    




