from django.shortcuts import render, redirect
from .models import User, Contact, Address
from restaurant.models import Restaurant
from menu.models import Menu
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required 
from django.db.models import Avg
from order.models import Order, OrderItem
from django.http import JsonResponse
from django.urls import reverse
from twilio.rest import Client
from django.conf import settings
from datetime import datetime


# Rendering home page with all food items.
def home(request):
    try:
        if request.user.is_authenticated:
            # Retrieve the user's city based on their address
            userAddress, created = Address.objects.get_or_create(user=request.user, primary=True)

            # Get all restaurants in the user's city
            if not created:
                userCityRestaurants = Restaurant.objects.filter(city=userAddress.city)
                
            if not userAddress.city:
                userCityRestaurants = Restaurant.objects.all()
        else:
            # Show all menu items to anonymous users
            userCityRestaurants = Restaurant.objects.all()

        # Get the search term from the request (either food name or restaurant name)
        foodNameRestaurant = request.GET.get('search-food-restaurant')

        price = request.GET.get('price')
        url = ""
        restaurantUrl = ""

        # Build the base queryset
        foodRestaurant = Menu.objects.filter(restaurant__in=userCityRestaurants)

        # Apply filters based on user input
        if foodNameRestaurant:
            # Check if the search term corresponds to a restaurant
            restaurant = Restaurant.objects.filter(name__icontains=foodNameRestaurant).first()

            # If it's a restaurant, filter menus by that restaurant
            if restaurant:
                foodRestaurant = foodRestaurant.filter(restaurant=restaurant)
                restaurantUrl = restaurant
                restaurantUrl = restaurantUrl
                
            else:
                # If it's not a restaurant, assume it's a food item and filter menus by name
                foodRestaurant = foodRestaurant.filter(name__icontains=foodNameRestaurant)

        elif price:
            foodRestaurant = foodRestaurant.filter(price__lte=price)
            url = price

        # Add average rating to each menu item
        foodRestaurant = foodRestaurant.annotate(averageRating=Avg('review__rating'))

        # Prepare the context to pass data to the template
        context = {
            'foods': foodRestaurant,
            'url' : url,
            'restaurantUrl': restaurantUrl
        }

    except Address.DoesNotExist:
        # Handle the case where the user does not have an associated address
        context = {
            'foods': foodRestaurant,
            'url' : url,
            'restaurantUrl': restaurantUrl
        }

    return render(request, 'home.html', context)

# Rendering profile page.
def profile(request):
    if not request.user.is_authenticated:
        return redirect("/login/") 

    user = request.user
    pri =  request.POST.get('primary') 

    try:
        address = Address.objects.get(user=user, primary=pri)
    except Address.DoesNotExist:
        address = None

    if request.method == "POST":
        img = request.FILES.get('image')
        if img:
            user.profile = img
            user.save()
            return JsonResponse({'status': 'upload'})
        if pri:
            address = Address.objects.get(user=user, primary=pri)
            user.first_name = request.POST.get('fname', '')
            user.last_name = request.POST.get('lname', '')
            user.email = request.POST.get('email', '')
            user.mobile = request.POST.get('mobile', '')
            # user.profile = request.FILES.get('wizard-picture', '')

            address.state = request.POST.get('state', '')
            address.city = request.POST.get('city', '')
            address.area = request.POST.get('area', '')
            address.zipcode = request.POST.get('zipcode', '')
            address.house_no = request.POST.get('house', '')
            address.category = request.POST.get('category', '')

            user.save()
            address.save()
            return JsonResponse({'status':'profileUpdate'})
        else:
            address = Address.objects.create(user=user, primary=False) 
            address.state = request.POST.get('state', '') 
            address.city = request.POST.get('city', '') 
            address.area = request.POST.get('area', '') 
            address.zipcode = request.POST.get('zipcode', '') 
            address.house_no = request.POST.get('house', '1') 
            address.category = request.POST.get('category', '') 
            address.save() 
            
            address = Address.objects.filter(user=user).values()
            address = list(address)

            return JsonResponse({'status':'profileUpdate', 'address':address})
    
    userAddress, created = Address.objects.get_or_create(user=request.user, primary=True)
    context = {
        'user_profile' : user,
        'user_address' : userAddress
    }

    if request.user.user_type == "Customer":
        return render(request, 'account/profile.html', context)
    
    elif request.user.user_type == "Foodprovider":
        context['resturant_data'] = Restaurant.objects.filter(user=request.user)
        return render(request, 'restaurant_admin/profile.html', context)
    
    else:
        return render(request, 'account/profile.html', context)

# Rendering signup page & And registering user.
def signUp(request): 
    if request.method == 'POST': 
        name = request.POST.get('uname') 
        email = request.POST.get('email') 
        mobile = request.POST.get('mobile') 
        userType = request.POST.get('utype') 
        password1 = request.POST.get('pwd') 
        password2 = request.POST.get('pwdc') 

        if name and User.objects.filter(username=name).exists():
            return JsonResponse({'status':'userExist'})

        if email and User.objects.filter(email=email).exists():
            return JsonResponse({'status':'emailExist'})

        if mobile and User.objects.filter(mobile=mobile):
            return JsonResponse({'status':'mobileExist'})

        if password1 == password2:
            newUser = User.objects.create(username=name, email=email, mobile=mobile, user_type=userType)
            newUser.set_password(password1)
            newUser.save()

            if userType == "Customer":
                return JsonResponse({'status':'createAccount'})
            
            elif userType == "Foodprovider":
                return JsonResponse({'status':'createAccount'})

        else:
            # Error handling for password mismatch
            return JsonResponse({'status':'passwordNotMatch'})

    return render(request, 'account/signup.html')

# Rendering signin page & And authenticate user.
def signIn(request):
    if request.method == 'POST':
        uname = request.POST.get('uname')
        pwd = request.POST.get('pwd')

        user = authenticate(request, username=uname, password=pwd)

        if user is not None:
            if user.user_type == "Customer":
                login(request, user)

                # request.session["username"] = uname
                # request.session["password"] = pwd
                return JsonResponse({"status":"signIn"})
                
            elif user.user_type == "Foodprovider":
                login(request, user)
                print("ok")
                return JsonResponse({'status':'signInAdmin'})
                
            elif user.user_type == "Driver":
                login(request, user)
                return redirect('/')  # Need to set the correct path
        else:
            return JsonResponse({'status':'invalidUser'})

    return render(request, 'account/login.html')

# Sent Number to verify
def verifyNumber(request):
    if request.method == "POST":
        phone_no = request.POST.get('phone_no')
        uname = request.session.get("username")
        user = User.objects.get(username=uname)
        user.mobile = phone_no
        user.save()
        return redirect(reverse('verify', kwargs={'phoneNo': phone_no}))
    
    return render(request, 'account/verifyNumber.html')


# Get token's from the settings.py
account_sid = settings.ACCOUNT_SID
auth_token = settings.AUTH_TOKEN
verify_sid = settings.VERIFY_SID

client = Client(account_sid, auth_token) 

# Verify Number
def verify(request, phoneNo):
    if request.method == "POST":
        code = request.POST.get('code')

        # Check otp is still valid or not
        # Get the otp creation time from the session
        now = datetime.now()
        otpGetTime = now.strftime("%H:%M:%S")
        otpCreateTime = request.session.get("otpCreationTime")

        if(otpCreateTime):
            otp_create_time = datetime.strptime(otpCreateTime, "%H:%M:%S")
            otp_enter_time = datetime.strptime(otpGetTime, "%H:%M:%S")
            time_difference = otp_enter_time - otp_create_time
            seconds_difference = int(time_difference.total_seconds())

            if seconds_difference < 40:
                verification_check = client.verify.services(verify_sid).verification_checks.create(
                    to=f"+91{phoneNo}",
                    code=code
                )

                if verification_check.status == "approved": 
                    user = authenticate( 
                        request, 
                        username=request.session.get('username'), 
                        password=request.session.get('password') 
                    ) 
                    login(request, user)
                    
                    return redirect('index')
                else:
                    return redirect('/login/')
            else:
                return redirect('/login/') 

    # Store otp creation time and store it in session
    now = datetime.now() 
    request.session["otpCreationTime"] = now.strftime("%H:%M:%S")
    
    verification = client.verify.services(verify_sid).verifications.create(
        to=f"+91{phoneNo}",
        channel='sms' 
    )
    return render(request, 'account/verify.html')


# Rendering orders page & showing my order history
@login_required(login_url='/login/')
def orders(request):
    # Only valid customer can access this page
    if not request.user.user_type == "Customer":
        return redirect("/login/")
    
    userOrders = Order.objects.filter(user=request.user)

    context = {
        'userOrders' : userOrders
    }

    return render(request, 'account/orders.html', context)

# Rendering orderInfo page & showing information of individual order.
def orderInfo(request, id):

    myOrders = OrderItem.objects.filter(order__order_id=id)
    
    order = Order.objects.get(order_id=id)
    deliveryAdd = order.deliveryAddress
    
    context = {
        'myOrders' : myOrders,
        'deliveryAdd': deliveryAdd
    }
    return render(request, 'account/orderInfo.html', context)

# Function to logout user 
@login_required(login_url='/login/') 
def logOut(request): 
    if request.user.user_type == "Customer":
        logout(request) 
        return redirect('/')
    elif request.user.user_type == "Foodprovider":
        logout(request)
        return redirect('/foodprovider/adminSignin/')
    else:
        logout(request) 
        return redirect('/')

# Contact page for everyone
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        contact = Contact.objects.create(name=name, email=email, subject=subject, message=message)
        contact.save()
        return JsonResponse({'status': 'Save'})
    
    return render(request, 'contact.html')