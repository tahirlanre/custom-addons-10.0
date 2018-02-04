# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _

class product_template(models.Model):
    _inherit = 'product.template'
    
    type = fields.Selection(default='product')