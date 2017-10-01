# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountMove(models.Model):
    _inherit = "account.move"
    
    @api.model
    def create(self, vals):
        move = super(AccountMove, self).create(vals)
        move.post()
        return move