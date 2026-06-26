from lictor.core import analyze_email, analyze_file, analyze_text, analyze_url

print(analyze_url("http://bit.ly/a?token=1")["level"])
print(analyze_email(sender="support@hotmail.com", claimed="Microsoft", subject="Cuenta bloqueada", body="Confirma tu clave urgente")["level"])
print(analyze_text("Soy tu nieto cambié de número necesito plata urgente no le digas a nadie")["level"])
