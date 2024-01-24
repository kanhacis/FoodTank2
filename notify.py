# from notifypy import Notify

# # Create a notification object
# notification = Notify()

# # Set the title and message for the notification
# notification.title = "Task Reminder"
# notification.message = "http://127.0.0.1:8000/"

# # Set the urgency level
# # notification.urgency = "critical"

# # Set the path to the notification icon
# notification.icon = "/home/cis/Downloads/notification.png"

# # Set the timeout for the notification 
# # notification.timeout = 10000 

# # Display the notification 
# notification.send()  

# import pdfkit

# pdfkit_options = {
#     'wkhtmltopdf': '/usr/bin/wkhtmltopdf',  # Specify the correct path here
# }

# pdfkit.from_file('test.html', 'out.pdf', options=pdfkit_options)


from weasyprint import HTML

html_file_path = 'test.html'

output_pdf = 'output.pdf'
HTML(filename=html_file_path).write_pdf(output_pdf)

# print(f'PDF file "{output_pdf}" has been created.')

# HTML(string=html_code).write_pdf(output_pdf)