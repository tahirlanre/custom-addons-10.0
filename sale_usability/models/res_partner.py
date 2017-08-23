# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo import exceptions

import odoo.addons.decimal_precision as dp

class Partner(models.Model):
    _inherit = 'res.partner'
    
    @api.multi
    def name_get(self):
        res = super(Partner,self).name_get()
        data = []
        for partner in self:
            name = ''
            if partner.ref:
                name += '['
                name += partner.ref
                name += '] '
            name += partner.name or ""
            data.append((partner.id, name))
        return data
        
    @api.model
    def create(self,vals):
        if vals.get('ref'):
            if self.search([('ref','=',vals['ref'])]):
                raise exceptions.Warning('Customer/Supplier code already exists')
        res = super(Partner,self).create(vals)
        return res
    
    ref = fields.Char(string='Internal Reference', required=True, index=True)   #make ref compulsory when creating a customer