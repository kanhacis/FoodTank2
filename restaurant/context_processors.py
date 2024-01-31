from .models import Restaurant, Notification 


def navbar_context(request):
    # Get restaurant order notification data
    try:
        restaurant = Restaurant.objects.get(user=request.user)
        notification = Notification.objects.filter(restaurant=restaurant)

        return {'navbar_data': notification}
    except:
        return {'navbar_data': 1}