# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _

class product_category(models.Model):
    _inherit = 'product.category'
    _order = 'id,name'