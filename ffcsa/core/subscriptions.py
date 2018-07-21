import stripe
import datetime

from django.utils import formats
from mezzanine.utils.email import send_mail_template
from mezzanine.conf import settings

from ffcsa.core.utils import get_friday_pickup_date, ORDER_CUTOFF_DAY, get_order_week_start

stripe.api_key = settings.STRIPE_SECRET_KEY
SIGNUP_DESCRIPTION = 'FFCSA Signup Fee'


def charge_signup_fee_if_needed(user):
    if not user.profile.paid_signup_fee:
        if not user.profile.stripe_customer_id:
            raise AssertionError('Attempting to charge a signup fee, but user has no stripe customer id')

        stripe.Charge.create(
            amount=settings.SIGNUP_FEE_IN_CENTS,
            currency='usd',
            description=SIGNUP_DESCRIPTION,
            customer=user.profile.stripe_customer_id,
            statement_descriptor='FFCSA Signup Fee'
        )
        # we update the user.profile.paid_signup_fee when the payment goes through


def get_subscription_fee(type):
    if type == 'CC':
        return 3
    else:
        return 0


def update_subscription_fee(user):
    if not user.profile.stripe_subscription_id:
        raise AssertionError('Attempting to update a subscription but user doesnt have a subscription')

    subscription = stripe.Subscription.retrieve(user.profile.stripe_subscription_id)
    subscription.tax_percent = get_subscription_fee(user.profile.payment_method)
    subscription.save()


def update_stripe_subscription(user):
    amount = user.profile.monthly_contribution

    if amount is None:
        raise ValueError('Attempting to update a subscription but user monthly_contribution hasnt been set')
    if not user.profile.stripe_subscription_id:
        raise AssertionError('Attempting to update a subscription but user doesnt have a subscription')
    if not user.profile.stripe_customer_id:
        raise AssertionError('Attempting to update a subscription but user has not stripe customer id')

    tax_percent = get_subscription_fee(user.profile.payment_method)

    plan = stripe.Plan.create(
        amount=(amount * 100).quantize(0),  # in cents
        interval="month",
        interval_count=1,
        product=settings.STRIPE_PRODUCT_ID,
        currency="usd",
        nickname="{} Membership".format(user.get_full_name())
    )
    subscription = stripe.Subscription.retrieve(user.profile.stripe_subscription_id)
    subscription.tax_percent = tax_percent

    try:
        subscription.plan.delete()
    except stripe.error.InvalidRequestError:
        pass

    subscription.save()
    stripe.Subscription.modify(subscription.id,
                               items=[{
                                   'id': subscription['items']['data'][0].id,
                                   'plan': plan.id
                               }]
                               )


def create_stripe_subscription(user):
    amount = user.profile.monthly_contribution

    if amount is None:
        raise ValueError('Attempting to create a subscription but user monthly_contribution hasnt been set')
    if user.profile.stripe_subscription_id:
        raise AssertionError('Attempting to create a subscription but user already has a subscription')
    if not user.profile.stripe_customer_id:
        raise AssertionError('Attempting to create a subscription but user has not stripe customer id')

    tax_percent = get_subscription_fee(user.profile.payment_method)

    plan = stripe.Plan.create(
        amount=(amount * 100).quantize(0),  # in cents
        interval="month",
        interval_count=1,
        product=settings.STRIPE_PRODUCT_ID,
        currency="usd",
        nickname="{} Membership".format(user.get_full_name())
    )
    subscription = stripe.Subscription.create(
        customer=user.profile.stripe_customer_id,
        items=[
            {
                "plan": plan.id
            },
        ],

        # TODO integrate crypto
        tax_percent=tax_percent,
    )
    user.profile.stripe_subscription_id = subscription.id
    user.profile.save()

    charge_signup_fee_if_needed(user)


def send_first_payment_email(user):
    now = datetime.datetime.now()
    can_order_now = 1 <= now.weekday() <= ORDER_CUTOFF_DAY
    week_start = get_order_week_start()

    pickup = get_friday_pickup_date()
    if user.profile.drop_site and user.profile.drop_site.lower().strip() == 'farm':
        pickup = pickup + datetime.timedelta(1)

    context = {
        'pickup_date': formats.date_format(pickup, "D F d"),
        'drop_site': user.profile.drop_site,
        'can_order_now': can_order_now,
        'order_week_start': formats.date_format(week_start, "D F d"),
    }
    send_mail_template(
        "Welcome to the FFCSA!",
        "ffcsa_core/first_payment_email",
        settings.DEFAULT_FROM_EMAIL,
        user.email,
        context=context,
        fail_silently=False,
        addr_bcc=[settings.EMAIL_HOST_USER]
    )


def send_failed_payment_email(user, error, amount, date, payments_url):
    to = user.email if user else settings.ADMINS[0][1]
    context = {
        'error': error,
        'amount': amount,
        'date': date,
        'payments_url': payments_url
    }

    subject = "[{}] Payment Failed".format(settings.SITE_TITLE)
    if not user:
        subject += " - NO User Found"
    send_mail_template(
        subject,
        "ffcsa_core/failed_payment_email",
        settings.DEFAULT_FROM_EMAIL,
        to,
        context=context,
        fail_silently=False,
        addr_bcc=[settings.DEFAULT_FROM_EMAIL]
    )