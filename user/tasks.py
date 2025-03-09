from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_otp_email(email, otp):
    subject = "AI Attendance Login Code"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    # Render the HTML template with the OTP
    html_content = render_to_string("email/otp_email.html", {"otp": otp})
    text_content = strip_tags(html_content)  # Convert HTML to plain text

    # Create the email
    email_message = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
    email_message.attach_alternative(html_content, "text/html")

    # Send the email
    email_message.send()
