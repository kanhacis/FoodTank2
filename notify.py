from notifypy import Notify

# Create a notification object
notification = Notify()

# Set the title and message for the notification
notification.title = "Task Reminder"
notification.message = "http://127.0.0.1:8000/"

# Set the urgency level
# notification.urgency = "critical"

# Set the path to the notification icon
notification.icon = "/home/cis/Downloads/notification.png"

# Set the timeout for the notification 
# notification.timeout = 10000 

# Display the notification 
notification.send()  