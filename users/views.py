from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.contrib.auth import logout as log_out
from django.contrib.auth import login as log_in
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string

from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.conf import settings


from .forms import SignUpForm



########################################################################################################################


class TokenGenerator(PasswordResetTokenGenerator):
    pass


generate_token = TokenGenerator()

########################################################################################################################


def dashboard(request):
    return render(request, 'users/dashboard.html', {'title': "Tableau de bord"})


def videos_list(request):
    return render(request, 'users/videos_list.html', {'title': "Liste des vidéos"})


def comments_list(request):
    return render(request, 'users/comments_list.html', {'title': "Liste des commentaires"})



def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            password = form.cleaned_data.get('password1')
            email = form.cleaned_data.get('email')

            user = User.objects.create_user(username=username, email=email)
            user.set_password(password)
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = False
            user.save()

            current_site = get_current_site(request)

            email_subject = 'Activer votre compte'
            email_message = render_to_string(
                'registration/activate.html',
                {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': generate_token.make_token(user)
                }
            )

            email_sender = EmailMessage(
                email_subject,
                email_message,
                settings.EMAIL_HOST_USER,
                [email]
            )

            email_sender.send()

            messages.warning(
                request,
                "Merci de cliquer sur le lien envoyé dans votre boite mail !",
                fail_silently=True
            )
            return redirect('users:login')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {
        'form': form,
        'title': "Inscription",
        'header_title': "Inscription", })


def logout(request):
    log_out(request)
    messages.info(request, "On espere vous revoir bientot !", fail_silently=True)
    return redirect("core:home")


def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        try:
            user_inst = User.objects.get(username=request.POST.get("username"))
            user_active = user_inst.is_active
            if user_active is False:
                messages.warning(
                    request,
                    "Merci de cliquer sur le lien envoyé dans votre boite mail !",
                    fail_silently=True
                )
                return redirect('users:login')
            else:
                if form.is_valid():
                    username = form.cleaned_data.get('username')
                    password = form.cleaned_data.get('password')
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        log_in(request, user)
                        messages.info(request, f"Bienvenue {username} !", fail_silently=True)
                        return redirect('/admin')

                else:
                    messages.error(request, "Nom d'utilisateur ou mot de passe incorrect", fail_silently=True)
        except:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect", fail_silently=True)
    form = AuthenticationForm()
    return render(request, 'registration/login.html', {"form": form, 'title': "Connexion"})


def account_activation(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

    # TODO : check doesnotexist
    except User.DoesNotExist:
        user = None

    if user is not None and generate_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            request,
            "Votre compte à été validé avec succès",
            fail_silently=True
        )
        return redirect('core:home')
    return render(request, 'registration/activate_failed.html', status=401)

