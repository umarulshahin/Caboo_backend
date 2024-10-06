
from celery import shared_task
from django.core.mail import send_mail


@shared_task(bind=True)
def send_email_task(self, subject, message, from_email, recipient_list):
    print('email send is woring')
    try:
        send_mail(subject, message, from_email, recipient_list,fail_silently=False)
        return "success"
    except Exception as e:
        self.retry(exc=e)
        return "fails"
