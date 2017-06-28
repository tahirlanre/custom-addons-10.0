# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models

import odoo.addons.decimal_precision as dp

class Partner(models.Model):
    _inherit = 'res.partner'
    
    @api.one
    @api.depends('debit', 'credit')
    def _get_balance(self):
        for partner in self:
            partner.balance = self.credit - self.debit
            
    balance = fields.Float(
        compute='_get_balance',
        string='Balance', readonly=True,
        digits=dp.get_precision('Account'))