from django.core.mail import get_connection, send_mail
from django.core.mail.message import EmailMessage


def envoyerMailPermAgora(sujet, message, destinataires):
    my_host = 'smtp.gmail.com'
    my_port = 587
    my_username = 'XXXXX'
    my_password = 'XXXXX'
    my_use_tls = True
    with get_connection(
            host=my_host,
            port=my_port,
            username=my_username,
            password=my_password,
            use_tls=my_use_tls
    ) as connection:
        EmailMessage(sujet, message, my_username + '@gmail.com', destinataires,
                     connection=connection).send()
