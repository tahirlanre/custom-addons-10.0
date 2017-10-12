# -*- coding: utf-8 -*-

from odoo import models, api, fields, _

class ResPartner(models.Model):
    _inherit = "res.partner"    
    
    sales_rep_id = fields.Many2one('sales.rep', 'Contact Person')
    