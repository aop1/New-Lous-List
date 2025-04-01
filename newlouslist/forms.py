from django.db import models
from django import forms
from allauth.socialaccount.forms import SignupForm
from allauth.account.models import EmailAddress

class CustomSocialSignupForm(SignupForm):

    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control w-75", "placeholder": "Username"}), max_length=30, )
    email = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control-plaintext"}), )
    first_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}), max_length=30, )
    last_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}), max_length=30, label="Last name")

    def save(self, request):

        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super(CustomSocialSignupForm, self).save(request)

        # Add your own processing here.
        # Uncomment if email is displayed as form in signup page
        if self.cleaned_data["email"] != user.email:
            EmailAddress.objects.get(email=self.cleaned_data["email"]).delete()
        # user.first_name = self.cleaned_data["first_name2"]
        # user.save()

        # You must return the original result.
        return user
