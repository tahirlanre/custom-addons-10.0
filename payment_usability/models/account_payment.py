# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from odoo import api, models, fields

class account_payment(models.Model):
    _inherit = "account.payment"
    
    @api.onchange('partner_id')
    def _set_payment_info(self):
        self.payment_info = self.partner_id.name
    
    payment_info = fields.Text(string='Payment Details', help='Details of the payment e.g teller no, customer name')
    