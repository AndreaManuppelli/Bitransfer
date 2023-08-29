from __future__ import absolute_import, unicode_literals
from celery import shared_task
from ...models import Payments, IncorrectPayments, PurchasedPlans, CustomUser
from django.conf import settings
from django.utils import timezone
from ...wallet import Wallet
import requests
from django.db.models import F
from django.core.management.base import BaseCommand
import time

class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        while True:
            self.stdout.write('Running tasks...')
            self.update_payments()
            time.sleep(1)  # Aspetta 10 secondi prima di ripetere


    def update_payments(self):

        try:

            # Get time threshold from settings
            time_threshold = timezone.now() - settings.PAYMENTS_TIME_RANGE

            # Create wallet instance
            walletBTC = Wallet.Btc(user=settings.BTC_RPC_USER, password=settings.BTC_RPC_PSW, wallet_name=settings.BTC_WALLET_NAME)

            #-------------> UPDATE MAIN PENDING PAYMENTS <--------------#

            # Get all active payment requests
            payment_requests = Payments.objects.filter(creation__gte=time_threshold).filter(paid=False).filter(incorrect_payment=False)

            # Iterate and manage each 
            for i in payment_requests:
                
                # Check if slected coin is bitcoin
                if i.coin == "bitcoin":

                    # Get amount and confirmations from address
                    data = walletBTC.get_address_balance(i.address)

                    # Assign amount to variable
                    amount = data["amount"]

                    # Assign cofirmations to variable
                    confirmations = data["confirmations"]
                    
                    # Verify that the payment has been detected
                    if confirmations != None:

                        if confirmations <= 3:
                            # Update tx confirmations into db
                            Payments.objects.filter(id=i.id).update(tx_confirmations=confirmations)

                        # if payment is in mempool assign uncofrimed amount
                        if confirmations < settings.MIN_BTC_CONFIRMATIONS:

                            # Assign unconfirmed amount
                            unconfirmed = amount

                            # Assign confirmed amount
                            confirmed = 0

                        
                        # if payment is in confirmed assign confirmed amount
                        elif confirmations >= settings.MIN_BTC_CONFIRMATIONS:

                            # Assign confirmed amount
                            confirmed = amount

                            # Assign unconfirmed amount
                            unconfirmed = 0

                            # Update into db confirmed amount recived
                            Payments.objects.filter(address=i.address).update(recived=amount)

                        # Check if unconfirmed or confirmed amount are assigned
                        if unconfirmed or confirmed:

                            # Check that the unconfirmed funds received are greater than 0
                            if unconfirmed > 0:
                                
                                # Check if uncofirmed funds are greater than the amount required
                                if unconfirmed >= i.amount and i.paid_not_confirmed == False:
                                    
                                    # Mark this payment paid but not confirmed into db
                                    Payments.objects.filter(address=i.address).update(paid_not_confirmed=True)

                                    # Update unconfirmed funds amount into db
                                    Payments.objects.filter(address=i.address).update(recived_unconfirmed=unconfirmed)

                                # Check if uncofirmed funds are greater than the amount required
                                elif unconfirmed < i.amount and i.paid_not_confirmed_incorrect == False:

                                    # Mark this payment paid but incorrect and not confirmed into db
                                    Payments.objects.filter(address=i.address).update(paid_not_confirmed_incorrect=True)

                                    # Update unconfirmed funds amount into db
                                    Payments.objects.filter(address=i.address).update(recived_unconfirmed=unconfirmed)

                            # Check if confrmed funds are greater than 0 and check if paid field into db are marked False
                            elif confirmed > 0 and i.paid == False:
                                
                                # Check if confirmed funds for this payment are greater than expected amount
                                if confirmed >= i.amount:

                                    # Mark payment paid into db
                                    Payments.objects.filter(address=i.address).update(paid=True)
                                
                                # Check if confirmed funds for this payment are less than expected amount
                                elif confirmed < i.amount and i.incorrect_payment == False:

                                    # Mark this payment like incorrect (less than expected amount)
                                    Payments.objects.filter(address=i.address).update(incorrect_payment=True)

                                    # Create instance incorrect payment to enable the funds to be recovered
                                    instance = IncorrectPayments(id=i.id, coin=i.coin, amount=i.amount,
                                                                returned=False, recived=confirmed)
                                    
                                    # Save record into db
                                    instance.save()

                                    # Check if the url to ping is present
                                    if i.signal_url:
                                        
                                        # Ping signal url
                                        try:
                                            requests.get(i.signal_url, timeout=5)
                                        except:
                                            pass
            #-------------> END <--------------#



            #-------------> UPGRADE SUBSCRIPTION PLANS / MANAGE PAYMENTS <--------------#

            active_plan_pending_payments = PurchasedPlans.objects.filter(creation__gte=time_threshold).filter(paid=False).filter(incorrect_payment=False)

            # Iterate and manage each active plan purchase request
            for i in active_plan_pending_payments:
                # Get amount and confirmations from address
                    data = walletBTC.get_address_balance(i.address)

                    # Assign amount to variable
                    amount = data["amount"]

                    # Assign cofirmations to variable
                    confirmations = data["confirmations"]

                    # Verify that the payment has been detected
                    if confirmations != None:
                    
                        # if payment is confirmed assign confirmed amount
                        if confirmations >= settings.MIN_BTC_CONFIRMATIONS:
                            # Assign confirmed amount
                            confirmed = 0

                            
                        # if payment is not confirmed assign confirmed amount
                        else:

                            # Assign confirmed amount
                            confirmed = amount


                            # Update into db confirmed amount recived
                            PurchasedPlans.objects.filter(address=i.address).update(recived=amount)

                        # Check if confirmed amount are assigned
                        if confirmed:

                            # Check if confrmed funds are greater than 0 and check if paid field into db are marked False
                            if confirmed > 0 and i.paid == False and i.incorrect_payment == False:

                                # Check if confirmed funds for this payment are greater than expected amount
                                if confirmed >= i.amount:

                                    # Mark payment paid into db
                                    PurchasedPlans.objects.filter(address=i.address).update(paid=True)

                                    # Filter corresponding plan duration from plans in settings
                                    corresponding_plan_duaration = [d for d in settings.USER_PLANS_LIST if d['id'] == i.plan_id][0]["plan_duration"]

                                    # Get user
                                    user = CustomUser.objects.filter(username=i.username_buyer)

                                    # Insert datetime payment intop db
                                    PurchasedPlans.objects.filter(address=i.address).update(datetime_payment_confirmed=timezone.now())

                                    # Set new plan into db
                                    user.update(plan=i.plan_id)
                                    
                                    # Check if the user bought the plan they already had
                                    if user.first().plan == i.plan_id:
                                        # Increase user's plan duration
                                        user.update(remaining_days_plan=F('remaining_days_plan') + corresponding_plan_duaration)
                                    else:
                                        # Reset remaining days and apply the new plan duration because the new plan is different
                                        user.update(remaining_days_plan=corresponding_plan_duaration)
                                    

                                # Check if confirmed funds for this payment are less than expected amount
                                elif confirmed < i.amount:
                                    # Get user
                                    user = CustomUser.objects.filter(username=i.username_buyer)

                                    # Set new plan into db
                                    user.update(plan=i.plan_id)

                                    # Mark this payment like incorrect (less than expected amount)
                                    PurchasedPlans.objects.filter(address=i.address).update(incorrect_payment=True)

                                    # Create instance incorrect payment to enable the funds to be recovered
                                    instance = IncorrectPayments(id=i.id, coin="bitcoin", amount=i.amount,
                                                                returned=False, recived=confirmed)
                                    
                                    # Save record into db
                                    instance.save()
        except:
            pass        