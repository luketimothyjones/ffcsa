from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CharField
from django.db.models.base import ModelBase
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from future.builtins import str, super
from future.utils import with_metaclass
from mezzanine.conf import settings
from mezzanine.core.fields import FileField
from mezzanine.core.managers import DisplayableManager
from mezzanine.core.models import (ContentTyped, Displayable, Orderable,
                                   RichText)
from mezzanine.generic.fields import RatingField
from mezzanine.utils.models import AdminThumbMixin, upload_to

from cartridge.shop import fields, managers
from cartridge.shop.models import CartItem
from cartridge.shop.models.Priced import Priced
from cartridge.shop.models.Cart import Cart, update_cart_items


class BaseProduct(Displayable):
    """
    Exists solely to store ``DisplayableManager`` as the main manager.
    If it's defined on ``Product``, a concrete model, then each
    ``Product`` subclass loses the custom manager.
    """

    objects = DisplayableManager()

    class Meta:
        abstract = True


class Product(BaseProduct, Priced, RichText, ContentTyped, AdminThumbMixin):
    """
    Container model for a product that stores information common to
    all of its variations such as the product's title and description.
    """

    available = models.BooleanField(_("Available for purchase"),
                                    default=False)
    image = CharField(_("Image"), max_length=100, blank=True, null=True)
    categories = models.ManyToManyField("Category", blank=True,
                                        verbose_name=_("Product categories"))
    date_added = models.DateTimeField(_("Date added"), auto_now_add=True,
                                      null=True)
    related_products = models.ManyToManyField("self",
                                              verbose_name=_("Related products"), blank=True)
    upsell_products = models.ManyToManyField("self",
                                             verbose_name=_("Upsell products"), blank=True)
    rating = RatingField(verbose_name=_("Rating"))

    order_on_invoice = models.FloatField(default=0, null=True, blank=True,
                                         help_text="Order this product will be printed on invoices. If set, this will override the product's category order_on_invoice setting. This is a float number for more fine grained control. (ex. '2.1' will be sorted the same as if the product's parent category order_on_invoice was 2 & the product's category order_on_invoice was 1).")

    admin_thumb_field = "image"

    search_fields = {"variations__sku": 100}

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        unique_together = ("sku", "site")

    @property
    def vendor(self):
        return self.variations.first().vendor

    def save(self, *args, **kwargs):
        """
        Copies the price fields to the default variation when
        ``SHOP_USE_VARIATIONS`` is False, and the product is
        updated via the admin change list.
        """
        self.set_content_model()
        updating = self.id is not None
        super(Product, self).save(*args, **kwargs)
        if updating and not settings.SHOP_USE_VARIATIONS:
            default = self.variations.get(default=True)
            self.copy_price_fields_to(default)

    @models.permalink
    def get_absolute_url(self):
        """
        If get_category returns a category, we will return a hierarchical path for the product under the category page,
        otherwise return a non-hierarchical url.
        """
        category = self.get_category()
        if category:
            return ("shop_category_product", (), {
                "category_slug": category.get_raw_slug(),
                "slug": self.slug})
        return ("shop_product", (), {"slug": self.slug})

    def copy_default_variation(self):
        """
        Copies the price and image fields from the default variation
        when the product is updated via the change view.
        """
        default = self.variations.get(default=True)
        orig_sku = self.sku
        default.copy_price_fields_to(self)
        # TODO I don't think we need this anymore
        # setattr(self, "weekly_inventory", getattr(default, "weekly_inventory"))
        # setattr(self, "in_inventory", getattr(default, "in_inventory"))
        if default.image:
            self.image = default.image.file.name
        if not settings.SHOP_USE_VARIATIONS:
            update_cart_items(self, orig_sku)
        self.save()

    def get_category(self):
        """
        Returns the single category this product is associated with, or None
        if the number of categories is not exactly 1. We exclude the weekly
        example box category from this
        """
        categories = self.categories.all()
        # categories = self.categories.exclude(slug='weekly-box')
        if len(categories) == 1:
            return categories[0]
        return None


@python_2_unicode_compatible
class ProductImage(Orderable):
    """
    An image for a product - a relationship is also defined with the
    product's variations so that each variation can potentially have
    it own image, while the relationship between the ``Product`` and
    ``ProductImage`` models ensures there is a single set of images
    for the product.
    """

    file = FileField(_("Image"), max_length=255, format="Image",
                     upload_to=upload_to("shop.ProductImage.file", "product"))
    description = CharField(_("Description"), blank=True, max_length=100)
    product = models.ForeignKey("Product", related_name="images",
                                on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Image")
        verbose_name_plural = _("Images")
        order_with_respect_to = "product"

    def __str__(self):
        value = self.description
        if not value:
            value = self.file.name
        if not value:
            value = ""
        return value


@python_2_unicode_compatible
class ProductOption(models.Model):
    """
    A selectable option for a product such as size or colour.
    """
    type = models.IntegerField(_("Type"),
                               choices=settings.SHOP_OPTION_TYPE_CHOICES)
    name = fields.OptionField(_("Name"))

    objects = managers.ProductOptionManager()

    def __str__(self):
        return "%s: %s" % (self.get_type_display(), self.name)

    class Meta:
        verbose_name = _("Product option")
        verbose_name_plural = _("Product options")


class ProductVariationMetaclass(ModelBase):
    """
    Metaclass for the ``ProductVariation`` model that dynamcally
    assigns an ``fields.OptionField`` for each option in the
    ``SHOP_PRODUCT_OPTIONS`` setting.
    """

    def __new__(cls, name, bases, attrs):
        # Only assign new attrs if not a proxy model.
        if not ("Meta" in attrs and getattr(attrs["Meta"], "proxy", False)):
            for option in settings.SHOP_OPTION_TYPE_CHOICES:
                attrs["option%s" % option[0]] = fields.OptionField(option[1])
        args = (cls, name, bases, attrs)
        return super(ProductVariationMetaclass, cls).__new__(*args)


@python_2_unicode_compatible
class ProductVariation(with_metaclass(ProductVariationMetaclass, Priced)):
    """
    A combination of selected options from
    ``SHOP_OPTION_TYPE_CHOICES`` for a ``Product`` instance.
    """

    product = models.ForeignKey("shop.Product", related_name="variations",
                                on_delete=models.CASCADE)
    default = models.BooleanField(_("Default"), default=False)
    image = models.ForeignKey("ProductImage", verbose_name=_("Image"),
                              null=True, blank=True, on_delete=models.SET_NULL)

    vendor = models.CharField(blank=True, max_length=255)

    objects = managers.ProductVariationManager()

    class Meta:
        ordering = ("-default",)

    def __str__(self):
        """
        Display the option names and values for the variation.
        """
        options = []
        for field in self.option_fields():
            name = getattr(self, field.name)
            if name is not None:
                option = u"%s: %s" % (field.verbose_name, name)
                options.append(option)
        result = u"%s %s" % (str(self.product), u", ".join(options))
        return result.strip()

    def save(self, *args, **kwargs):
        """
        Use the variation's ID as the SKU when the variation is first
        created.
        """
        super(ProductVariation, self).save(*args, **kwargs)
        if not self.sku:
            self.sku = self.id
            self.save()

    def get_absolute_url(self):
        return self.product.get_absolute_url()

    def validate_unique(self, *args, **kwargs):
        """
        Overridden to ensure SKU is unique per site, which can't be
        defined by ``Meta.unique_together`` since it can't span
        relationships.
        """
        super(ProductVariation, self).validate_unique(*args, **kwargs)
        if self.__class__.objects.exclude(id=self.id).filter(
                product__site_id=self.product.site_id, sku=self.sku).exists():
            raise ValidationError({"sku": _("SKU is not unique")})

    @classmethod
    def option_fields(cls):
        """
        Returns each of the model fields that are dynamically created
        from ``SHOP_OPTION_TYPE_CHOICES`` in
        ``ProductVariationMetaclass``.
        """
        all_fields = cls._meta.fields
        return [f for f in all_fields if isinstance(f, fields.OptionField) and
                not hasattr(f, "translated_field")]

    def options(self):
        """
        Returns the field values of each of the model fields that are
        dynamically created from ``SHOP_OPTION_TYPE_CHOICES`` in
        ``ProductVariationMetaclass``.
        """
        return [getattr(self, field.name) for field in self.option_fields()]

    def live_num_in_stock(self):
        """
        Returns the live number in stock, which is
        ``self.num_in_stock - num in carts``. Also caches the value
        for subsequent lookups.
        """
        if self.num_in_stock is None:
            return None
        if not hasattr(self, "_cached_num_in_stock"):
            num_in_stock = self.num_in_stock
            carts = Cart.objects.current()
            items = CartItem.objects.filter(sku=self.sku, cart__in=carts)
            aggregate = items.aggregate(quantity_sum=models.Sum("quantity"))
            num_in_carts = aggregate["quantity_sum"]
            if num_in_carts is not None:
                num_in_stock = num_in_stock - num_in_carts
            self._cached_num_in_stock = num_in_stock
        return self._cached_num_in_stock

    def has_stock(self, quantity=1):
        """
        Returns ``True`` if the given quantity is in stock, by checking
        against ``live_num_in_stock``. ``True`` is returned when
        ``num_in_stock`` is ``None`` which is how stock control is
        disabled.
        """
        live = self.live_num_in_stock()
        return live is None or quantity == 0 or live >= quantity

    def update_stock(self, quantity):
        """
        Update the stock amount - called when an order is complete.
        Also update the denormalised stock amount of the product if
        this is the default variation.
        """
        if self.num_in_stock is not None:
            self.num_in_stock += quantity
            self.save()
            if self.default:
                self.product.num_in_stock = self.num_in_stock
                self.product.save()