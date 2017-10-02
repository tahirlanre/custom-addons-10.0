# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    nb_print = fields.Integer(string='Number of Print', readonly=True, copy=False, default=0)
    
    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.ensure_one()
        self.sent = True
        printed_nb = self.nb_print
        if printed_nb == 0 or self.env.user.has_group('account.group_account_manager'):
            self.nb_print = printed_nb + 1
            return self.env['report'].get_action(self, 'houseaffairs_custom_invoice.report_invoice')
        else:
            return False
            