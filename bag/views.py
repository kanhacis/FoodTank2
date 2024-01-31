from django.shortcuts import render, redirect
from menu.models import Menu
from .models import Bag, BagItem
from user.models import Address
from django.http import JsonResponse, HttpResponse
import os
from weasyprint import HTML
from django.template.loader import get_template


# Rendering add to bag page & write logic to add food in my bag.
def addToBag(request, id):
    # Check if the user is authenticated, if not, return a JSON response indicating the need for login
    if not request.user.is_authenticated or not request.user.user_type == "Customer":
        return redirect('/login/')

    # Get the menu item
    menuItem = Menu.objects.get(id=id)

    # Check if the user has a bag
    userBag, created = Bag.objects.get_or_create(user=request.user)

    # Check if the item is already in the bag
    bagItem, created = BagItem.objects.get_or_create(bag=userBag, item=menuItem)

    if created or bagItem.quantity == 0:
        # If the bag item is just created or the quantity is zero, set the quantity to 1
        bagItem.quantity = 1
    else:
        # Send response (item already existing)
        return JsonResponse({'status':'itemAddedAlready'})

    bagItem.save()
    
    # Get the count of bagItems
    bagItemCount = BagItem.objects.filter(bag=userBag).count()
    bagFoods = BagItem.objects.filter(bag=userBag)
    
    bagFoodsName = []
    for i in bagFoods:
        bagFoodsName.append(i.item.name)
    
    return JsonResponse({'status': 'itemAdded', 'bagItemCount':bagItemCount, 'bagFoodsName':bagFoodsName})


# Rendering view bag page where user can see their food bag.
def viewBag(request):
    if not request.user.is_authenticated or not request.user.user_type == "Customer":
        return redirect("/login/")
    
    try: # Handle error, when a user does not have any bag
        address = Address.objects.filter(user=request.user)
        userBag = Bag.objects.get(user=request.user)
        bagItems = BagItem.objects.filter(bag=userBag)

        if request.method == "GET" and 'id' in request.GET:
            item_id = request.GET.get('id')
            try:
                itemId = BagItem.objects.get(id=item_id)
                new_quantity = int(request.GET.get('quantity', 0))

                if new_quantity >= 1:
                    itemId.quantity = new_quantity
                    itemId.save()
                    price = itemId.item.price * itemId.quantity

                    # try start
                    total = 0 
                    for item in bagItems: 
                        item_quantity = int(item.quantity) 
                        item_price = int(item.item.price) 
                        total += item_quantity * item_price 
                    # try end
                    
                    return JsonResponse({'status': 'Increase', 'price':price, 'Final':total})
            except BagItem.DoesNotExist:
                pass
    except:
        return redirect('/foodprovider/restaurant/')

    total = 0 
    count = 0 
    for item in bagItems: 
        item_quantity = int(item.quantity) 
        item_price = int(item.item.price) 
        total += item_quantity * item_price 
        count += 1 

    context = { 
        'address': address,
        'bagItems': bagItems, 
        'total': total, 
        'count': count,
        'address2': Address.objects.get(user=request.user)
    } 

    # Example 1
    if request.method == "POST":
        html_content = render(request, "bag/inVoice.html", context).content
        
        # Generate PDF from HTML content
        pdf_output = 'inVoice.pdf'
        HTML(string=html_content.decode('utf-8')).write_pdf(pdf_output)

        # Open inVoice.pdf 
        with open(pdf_output, 'rb') as pdf_file:
            pdf_content = pdf_file.read()

        # Create an HttpResponse to send the file content 
        response = HttpResponse(pdf_content, content_type='application/pdf') 
        response['Content-Disposition'] = f'attachment; filename="{pdf_output}"' 
        os.remove(pdf_output) 
        return response         
    
    return render(request, "bag/basket.html", context)


# Write logic to deleting an foodItem which exist in my bag.
def deleteItem(request, id):
    # Check if the user is authenticated, if not, redirect them to the login page
    if not request.user.is_authenticated or not request.user.user_type=="Customer":
        return redirect("/login/")
    
    bagItem = BagItem.objects.get(id=id)
    price = bagItem.item.price * bagItem.quantity

    # Calculating total price for current bag items
    userBag = Bag.objects.get(user=request.user)
    bagItems = BagItem.objects.filter(bag=userBag)
    
    totalPrice = 0

    for item in bagItems: 
        item_quantity = int(item.quantity)
        item_price = int(item.item.price)
        totalPrice += item_quantity * item_price

    finalPrice = totalPrice - price
    
    bagItem.delete()

    count = 0 
    for item in bagItems: 
        count += 1 
    return JsonResponse({'status':'itemDeleted', 'finalPrice':finalPrice, 'totalItem':count}) 
