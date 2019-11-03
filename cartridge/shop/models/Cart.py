from collections import OrderedDict
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from future.builtins import super
from mezzanine.conf import settings

from cartridge.shop import managers
from ffcsa.core.models import Payment


class Cart(models.Model):
    last_updated = models.DateTimeField(_("Last updated"), null=True)

    # TODO change to fk?
    user_id = models.IntegerField(blank=False, null=False, unique=True)
    attending_dinner = models.IntegerField(blank=False, null=False, default=0)

    objects = managers.PersistentCartManager()

    def __iter__(self):
        """
        Allow the cart to be iterated giving access to the cart's items,
        ensuring the items are only retrieved once and cached.
        """
        if not hasattr(self, "_cached_items"):
            self._cached_items = self.items.all()
        return iter(self._cached_items)

    def add_item(self, variation, quantity):
        """
        Increase quantity of existing item if variation matches, otherwise create new.
        """
        if not self.user_id:
            raise Exception("You must be logged in to add products to your cart")
        if not self.pk:
            self.save()
        item, created = self.items.get_or_create(variation=variation)
        if created:
            variation.product.actions.added_to_cart()

        item.update_quantity(quantity)
        item.save()

    def clear(self):
        self.attending_dinner = 0
        self.items.all().delete()

    def over_budget(self, additional_total=0):
        return self.remaining_budget() < additional_total

    def remaining_budget(self):
        if not self.user_id:
            return 0

        User = get_user_model()
        user = User.objects.get(pk=self.user_id)

        ytd_order_total = self.objects.total_for_user(user)
        ytd_payment_total = Payment.objects.total_for_user(user)

        return ytd_payment_total - (ytd_order_total + self.total_price_after_discount())

    def discount(self):
        if not self.user_id:
            return 0

        User = get_user_model()
        user = User.objects.get(pk=self.user_id)

        if not user or not user.profile.discount_code:
            return 0

        return self.calculate_discount(user.profile.discount_code)

    def total_price_after_discount(self):
        return self.total_price() - self.discount()

    def has_items(self):
        """
        Template helper function - does the cart have items?
        """
        return len(list(self)) > 0

    def total_quantity(self):
        """
        Template helper function - sum of all item quantities.
        """
        return sum([item.quantity for item in self])

    def total_price(self):
        """
        Template helper function - sum of all costs of item quantities.
        """
        return sum([item.total_price for item in self])

    def skus(self):
        """
        Returns a list of skus for items in the cart. Used by
        ``upsell_products`` and ``calculate_discount``.
        """
        return [item.sku for item in self]

    def upsell_products(self):
        """
        Returns the upsell products for each of the items in the cart.
        """
        from cartridge.shop.models import Product
        if not settings.SHOP_USE_UPSELL_PRODUCTS:
            return []
        cart = Product.objects.filter(variations__sku__in=self.skus())
        published_products = Product.objects.published()
        for_cart = published_products.filter(upsell_products__in=cart)
        with_cart_excluded = for_cart.exclude(variations__sku__in=self.skus())
        return list(with_cart_excluded.distinct())

    def calculate_discount(self, discount):
        """
        Calculates the discount based on the items in a cart, some
        might have the discount, others might not.
        """
        from cartridge.shop.models import ProductVariation
        # Discount applies to cart total if not product specific.
        products = discount.all_products()
        if products.count() == 0:
            return discount.calculate(self.total_price())
        total = Decimal("0")
        # Create a list of skus in the cart that are applicable to
        # the discount, and total the discount for appllicable items.
        lookup = {"product__in": products, "sku__in": self.skus()}
        discount_variations = ProductVariation.objects.filter(**lookup)
        discount_skus = discount_variations.values_list("sku", flat=True)
        for item in self:
            if item.sku in discount_skus:
                total += discount.calculate(item.unit_price) * item.quantity
        return total


class CartItem(models.Model):
    cart = models.ForeignKey("shop.Cart", related_name="items", on_delete=models.CASCADE)
    variation = models.ForeignKey("shop.ProductVariation", related_name="+", on_delete=models.PROTECT, null=False)

    def __str__(self):
        return ''

    @property
    def image(self):
        return self.variation.image

    @property
    def description(self):
        return force_text(self.variation)

    @property
    def unit_price(self):
        return self.variation.price()

    @property
    def vendor_price(self):
        return self.variation.vendor_price

    @property
    def in_inventory(self):
        return self.variation.product.in_inventory

    @property
    def sku(self):
        return self.variation.sku

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    def get_absolute_url(self):
        return self.variation.product.get_absolute_url()

    @property
    def quantity(self):
        # The following check works in Django 2.2
        # if 'vendorproductvariation_set' not in self._state.fields_cache:
        if not hasattr(self, "_cached_quantity"):
            if 'vendors' not in getattr(self, '_prefetched_objects_cache', []) \
                    and not hasattr(self, self._meta.get_field('vendors').get_cache_name()):
                quantity = self.vendors.aggregate(quantity=models.Sum("quantity"))['quantity']
            else:
                quantity = sum([v.quantity for v in self.vendors.all()])
            self._cached_quantity = quantity
        return self._cached_quantity

    def update_quantity(self, quantity):
        remaining = quantity
        vendor_stock = OrderedDict()

        # Fetch the live_num_in_stock value for all possible vendors for this variation
        for vpv in self.variation.vendorproductvariation_set.all().order_by('_order'):
            vendor_stock[vpv.vendor_id] = vpv.live_num_in_stock()

        vendor_items = []
        for vendor_id, stock in vendor_stock.items():
            if stock is None:
                # If here, there is no limit. So we want this vendor
                vi, created = self.vendors.get_or_create(vendor_id=vendor_id)
                vi.quantity = vi.quantity + quantity
                vendor_items.append(vi)
                break
            else:
                if remaining > 0:
                    while remaining > 0:
                        qty = min(stock, quantity)
                        vi, created = self.vendors.get_or_create(vendor_id=vendor_id)
                        vi.quantity = vi.quantity + qty
                        vendor_items.append(vi)
                        remaining = remaining - qty
                    break
                else:
                    # TODO handle case where quantity is negative
                    # - when decreasing quantity, need to make sure we are updating the correct vendor if multiple. may need to update both & delete one, etc
                    raise NotImplementedError('Can not handle negative quantity')

        for item in vendor_items:
            if item.quantity < 0:
                raise AssertionError('Item quantity is negative')
            item.delete() if item.quantity == 0 else item.save()

        if hasattr(self, '_cached_quantity'):
            self._cached_quantity = self._cached_quantity + quantity

    def save(self, *args, **kwargs):
        super(CartItem, self).save(*args, **kwargs)

        # Check if this is the last cart item being removed
        if self.quantity == 0 and not self.cart.items.exists():
            self.cart.delete()


def update_cart_items(variation):
    """
    When an item has changed, update any items that are already in the cart
    """
    from ffcsa.core.budgets import clear_cached_budget_for_user_id
    carts = Cart.objects.filter(items__variation__sku=variation.sku)
    for cart in carts:
        clear_cached_budget_for_user_id(cart.user_id)
