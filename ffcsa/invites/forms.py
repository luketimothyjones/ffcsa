from django import forms
from django.core.exceptions import ValidationError
import stripe

from mezzanine.accounts import forms as base
from ffcsa.core.models import PHONE_REGEX

from .models import InvitationCode, InviteCodeIsOutOfDate, InviteCodeInvalidEmail


class ProfileForm(base.ProfileForm):
    username = None
    code = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        self.fields['phone_number'].validators.append(PHONE_REGEX)
        self.fields['phone_number_2'].validators.append(PHONE_REGEX)
        if self._signup:
            self.fields['email'].widget = forms.HiddenInput()

    def save(self, *args, **kwargs):
        user = super(ProfileForm, self).save(*args, **kwargs)

        if self._signup:
            # delete the code now that it has been successfully used
            code = InvitationCode.objects.get_code_from_key_if_valid(
                self.data['code'], self.data['email']
            )
            user.profile.drop_site = code.drop_site
            if code.non_subscribing_member:
                customer = stripe.Customer.create(
                    email=user.email,
                    description=user.get_full_name()
                )
                user.profile.stripe_customer_id = customer.id

            # only accepts CC payments
            user.profile.payment_method = 'CC'
            user.profile.ach_status = None
            user.profile.non_subscribing_member = code.non_subscribing_member
            code.delete()
            user.profile.save()

        return user

    def clean(self):
        if self._signup:
            errs = []
            try:
                email = self.cleaned_data['email']
            except KeyError:
                errs += self.errors['email']
                email = self.data['email']

            key = self.cleaned_data['code']
            code = None

            if not email:
                errs.append("A valid email is required")
                raise ValidationError(errs)

            try:
                code = InvitationCode.objects.get_code_from_key_if_valid(
                    key, email
                )
            except InviteCodeIsOutOfDate:
                pass
            except InviteCodeInvalidEmail:
                errs.append("Given email does not match the registered email for the invitation code")
                raise ValidationError(errs)

            if not code:
                errs.append("You must have a valid invitation code to create an account.")

            if errs:
                raise ValidationError(errs)
