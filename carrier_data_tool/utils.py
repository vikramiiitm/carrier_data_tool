from django.contrib.auth import get_user_model

def set_username(f_name: str) -> str:
    f_name = f_name.replace(' ', '')
    counter = 1
    User = get_user_model()
    while User.objects.filter(username=f_name).exists():
        f_name = f'{f_name}{str(counter)}'
        counter += 1
    return f_name.lower()