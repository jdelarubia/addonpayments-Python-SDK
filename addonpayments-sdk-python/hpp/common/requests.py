# -*- encoding: utf-8 -*-

import attr
from attr import ib as Field

from mixins import DictMixin
from utils import GenerationUtils
from validators import RequestValidator
from hpp.validators import HppValidator as Validator


@attr.s
class HppRequest(DictMixin):
    """
    Super class representing a request to be sent to HPP.
    This class contains all common attributes and functions for all other classes.

    You can consult the specific documentation of all HPP request fields on the website
    https://desarrolladores.addonpayments.com
    """

    # Mandatory fields
    merchant_id = Field(validator=RequestValidator.merchant_id)
    amount = Field(convert=str, validator=RequestValidator.amount)
    currency = Field(validator=RequestValidator.currency)
    auto_settle_flag = Field(validator=Validator.flag)

    # Mandatory fields with auto-generation
    timestamp = Field(default=None, validator=RequestValidator.timestamp)
    order_id = Field(default=None, validator=RequestValidator.order_id)

    # Mandatory fields generated later
    sha1hash = Field(default=None, validator=RequestValidator.sha1hash)

    # Optional fields
    account = Field(default='', validator=RequestValidator.account)
    comment1 = Field(default='', validator=Validator.comment)
    comment2 = Field(default='', validator=Validator.comment)
    shipping_code = Field(default='', validator=Validator.shipping_code)
    shipping_co = Field(default='', validator=Validator.country)
    billing_code = Field(default='', validator=Validator.billing_code)
    billing_co = Field(default='', validator=Validator.country)
    cust_num = Field(default='', validator=Validator.additional_info)
    var_ref = Field(default='', validator=Validator.additional_info)
    prod_id = Field(default='', validator=Validator.additional_info)
    hpp_lang = Field(default='', validator=Validator.lang)
    hpp_version = Field(default='')
    merchant_response_url = Field(default='', validator=Validator.url)
    card_payment_button = Field(default='', validator=Validator.card_payment_button)
    supplementary_data = Field(default={}, validator=Validator.supplementary_data)

    def __attrs_post_init__(self):
        """
        This method will be called after the class is fully initialized.
        Uses method to set auto-generate values if they have not been initialized
        """
        if not self.timestamp:
            self.timestamp = GenerationUtils().generate_timestamp()
        if not self.order_id:
            self.order_id = GenerationUtils().generate_order_id()

    def to_dict(self):
        """
        Overrides to_dict method from DictMixin to set the supplementary data
        :return: dict
        """
        result = {}
        for key, value in self.__dict__.items():
            # Add supplementary data into dict
            if key == 'supplementary_data':
                try:
                    for key_supp, value_supp in self.supplementary_data.items():
                        if key_supp not in self.__dict__.keys():
                            result[key_supp] = value_supp
                except AttributeError:
                    result[key.upper()] = value

            # Parse boolean fields to str '1' (True) or '0' (False)
            result_value = self.set_flags(key, value)
            if result_value:
                result[key.upper()] = result_value
        return result

    def hash(self, secret):
        """
        Creates the security hash from a number of fields and the shared secret.
        :param secret: string
        """
        # Get required values to generate HASH
        if int(self.card_storage_enable) == 1:
            str_hash = '{}.{}.{}.{}.{}.{}.{}'.format(
                self.timestamp, self.merchant_id, self.order_id, self.amount,
                self.currency, self.payer_ref, self.pmt_ref
            )
        else:
            str_hash = '{}.{}.{}.{}.{}'.format(
                self.timestamp, self.merchant_id, self.order_id, self.amount, self.currency
            )

        # Generate HASH
        gen_utl = GenerationUtils()
        self.sha1hash = gen_utl.generate_hash(str_hash, secret)
        return self.sha1hash
