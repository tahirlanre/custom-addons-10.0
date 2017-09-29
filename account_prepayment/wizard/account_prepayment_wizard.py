# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class PrepaymentConfirmationWizard(models.TransientModel):
    _name = "prepayment.confirmation.wizard"
    _description = "prepayment.confirmation.wizard"

    date = fields.Date('Account Date', required=True, help="Choose the period for which you want to automatically post the lines of running prepayments", default=fields.Date.context_today)

    @api.multi
    def prepayment_compute(self):
        self.ensure_one()
        context = self._context
        created_move_ids = self.env['account.prepayment'].compute_generated_entries(self.date, prepayment_type=context.get('prepayment_type'))

        return True
