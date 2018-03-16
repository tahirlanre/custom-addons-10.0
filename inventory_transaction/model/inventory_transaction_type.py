# -*- coding: utf-8 -*-
# © 2018 SITAYS (sitasyslimited@gmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields

class inventory_transaction_type(models.Model):
    _name = "inventory.transaction.type"
    
    name = fields.Char('Name')
    type = fields.Selection([('out_invoice','Customer Invoice'),('out_refund','Customer Refund'),('in_invoice','Vendor Bill'),('in_refund','Vendor Refund')])