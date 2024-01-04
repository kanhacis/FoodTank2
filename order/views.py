from django.shortcuts import render, redirect
from bag.models import Bag, BagItem
from .models import Order, OrderItem
from django.http import JsonResponse
from user.models import Address
import stripe
from django.conf import settings


# Place order
def placeOrder(request):
    # Get the payment method type from the user
    # Store data of [paymentMethod, city, area, zipcode, house_no]
    myData = []
    paymentMethod = ''
    if request.method == 'POST':
        payment = request.POST.get('payment', '')
        paymentMethod += payment

        city = request.POST.get('city', '')
        area = request.POST.get('area', '')
        zipcode = request.POST.get('zipcode', '')
        house_no = request.POST.get('house_no', '')
        myData.append([payment, city, area, zipcode, house_no])
    
    # Get the delivery address
    deliveryAdrs = Address.objects.get(user=request.user, city=myData[0][1].strip(), area=myData[0][2].strip(),
                                          zipcode=int(myData[0][3].strip()), house_no=int(myData[0][4].strip()))

    userBag = Bag.objects.get(user=request.user)
    bagItems = BagItem.objects.filter(bag=userBag)
    
    # Calculate the total bill
    sum = 0 
    for i in bagItems: 
        qunt = int(i.quantity)
        price = int(i.item.price)
        sum += qunt * price

    # Retrieve the current user's bag items
    bagItems = BagItem.objects.filter(bag__user=request.user)

    # Assuming the bag has items
    if bagItems.exists():
        # Assuming the bag items are associated with the same restaurant
        restaurant = bagItems.first().item.restaurant

        if myData[0][0].strip() != "Cash on delivery":
            url = 'http://127.0.0.1:8000/orders/'
            stripe.api_key = settings.STRIPE_SECRET_KEY

            orderSession = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                    'price_data': {
                        'currency': 'usd', # inr not support
                        'product_data': {'name' : 'None'},
                        'unit_amount': sum * 100,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                
                success_url = url + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url="http://127.0.0.1:8000/bag/view_bag/"
            )
            
            # Create an order associated with the restaurant
            # order = Order.objects.create(
            #     user = request.user,
            #     restaurant = restaurant,
            #     total_bill = sum,
            #     payment_method = myData[0][0].strip(),
            #     deliveryAddress = deliveryAdrs
            # )    

            # Create order items linked to the created order
            # for bag_item in bagItems:
            #     OrderItem.objects.create(
            #         order=order,
            #         item=bag_item.item,
            #         quantity=bag_item.quantity
            #     ) 

            # Clear the user's bag after placing the order
            # bagItems.delete()

            # Send url to redirect to the payment page
            return JsonResponse({'redirect': orderSession.url})
        else:
            # Create an order associated with the restaurant
            order = Order.objects.create(
                user = request.user,
                restaurant = restaurant,
                total_bill = sum,
                payment_method = myData[0][0].strip(),
                deliveryAddress = deliveryAdrs
            )    

            # Create order items linked to the created order
            for bag_item in bagItems:
                OrderItem.objects.create(
                    order=order,
                    item=bag_item.item,
                    quantity=bag_item.quantity
                ) 

            # Clear the user's bag after placing the order
            bagItems.delete()

            # Send success response
            return JsonResponse({"status": "success"})

    return redirect('/bag/view_bag/')