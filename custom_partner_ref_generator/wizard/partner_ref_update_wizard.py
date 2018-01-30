# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PartnerRefUpdate(models.TransientModel):
    _name = 'res.partner.ref.update'
    _description = 'Partner ref update'

    partner_id = fields.Many2one('res.partner')
    new_ref = fields.Char('New internal refrence (code)', required=True)

    @api.model
    def default_get(self, fields):
        res = super(PartnerRefUpdate, self).default_get(fields)
        if not res.get('partner_id') and self._context.get('active_id'):
            res['partner_id'] = self._context['active_id']
        return res

    @api.multi
    def update(self):
        self.ensure_one()
        for partner in self.partner_id:
            partner.ref = self.new_ref
