import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email and password for the sender
sender_email = "YOUR SENDER EMAIL"
sender_password = "YOUR APP PASSWORD"

def sendmail(recipient_email, temp_code, sender_email = "demoquick841@gmail.com", sender_password = "naqxmckyujmcssko"):

    # Create message container
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = "Account Password Recovery"

    # Email body
    body = f'''Your password has been changed to "{temp_code}". Please use it to Reset Password.'''

    # Attach the body to the message
    message.attach(MIMEText(body, 'plain'))

    # Connect to Gmail's SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    # Login to the Gmail account
    server.login(sender_email, sender_password)

    # Send the email
    server.sendmail(sender_email, recipient_email, message.as_string())

    # Close the SMTP server connection
    server.quit()
    return True