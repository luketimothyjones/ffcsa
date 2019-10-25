from _pydecimal import Decimal

from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from cartridge.shop import fields


class Priced(models.Model):
    """
    Abstract model with unit and sale price fields. Inherited by
    ``Product`` and ``ProductVariation`` models.
    """

    unit_price = fields.MoneyField(_("Member Price"))
    sale_id = models.IntegerField(null=True)
    sale_price = fields.MoneyField(_("Sale price"))
    sale_from = models.DateTimeField(_("Sale start"), blank=True, null=True)
    sale_to = models.DateTimeField(_("Sale end"), blank=True, null=True)
    sku = fields.SKUField(blank=True, null=True)
    num_in_stock = models.IntegerField(_("Number in stock"), blank=True,
                                       null=True)

    weekly_inventory = models.BooleanField(
        _("Weekly Inventory"), blank=False, default=True)
    in_inventory = models.BooleanField(
        _("FFCSA Inventory"), default=False, blank=False, null=False)
    vendor_price = fields.MoneyField(_("Vendor price"), blank=True, null=True)

    class Meta:
        abstract = True

    def on_sale(self):
        """
        Returns True if the sale price is applicable.
        """
        n = now()
        valid_from = self.sale_from is None or self.sale_from < n
        valid_to = self.sale_to is None or self.sale_to > n
        return self.sale_price is not None and valid_from and valid_to

    def has_price(self):
        """
        Returns True if there is a valid price.
        """
        return self.on_sale() or self.unit_price is not None

    def price(self):
        """
        Returns the actual price - sale price if applicable otherwise
        the unit price.
        """
        if self.on_sale():
            return self.sale_price
        elif self.has_price():
            return self.unit_price
        return Decimal("0")

    def copy_price_fields_to(self, obj_to):
        """
        Copies each of the fields for the ``Priced`` model from one
        instance to another. Used for synchronising the denormalised
        fields on ``Product`` instances with their default variation.
        """
        # TODO verify this copies vendor_price
        for field in Priced._meta.fields:
            if not isinstance(field, models.AutoField):
                setattr(obj_to, field.name, getattr(self, field.name))
        obj_to.save()