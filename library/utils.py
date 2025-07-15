from django.core.signing import TimestampSigner
from django.conf import settings
from django.core.mail import send_mail

signer = TimestampSigner()

def send_magic_link(user):
    token = signer.sign(user.pk)
    link = f"{settings.FRONTEND_URL}/auth/magic?token={token}"

    try:
        send_mail(
            subject="Welcome to My U Library",
            message=f"Click on the following link to access your account: {link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <p>Hello {user.first_name},</p>
                <p>Click on the following button to access your account:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{link}"
                       style="background-color: #007bff; color: white; padding: 12px 24px;
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Access my account
                    </a>
                </div>
                <p style="color: #666; font-size: 14px;">
                    If the button doesn't work, copy and paste this link in your browser:<br>
                    <a href="{link}" style="color: #007bff;">{link}</a>
                </p>
            </div>
            """
        )
        print(f"Email sent successfully to {user.email}")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False
