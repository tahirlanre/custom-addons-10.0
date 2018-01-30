# -*- coding: utf-8 -*-

from openerp import models, fields, api

import logging

_logger = logging.getLogger(__name__)

class res_company(models.Model):
    _inherit = "res.company"

    prefix_count = fields.Integer('Partner prefix count', help='# of letters from partner name to generate partner ref',default=3)
    partner_ref_padding = fields.Integer('Partner ref padding', default=4)

class res_partner(models.Model):
    _inherit = "res.partner"
    
    def get_prefix(self, name):
        count = self.env.user.company_id.prefix_count
        prefix = name[:count].upper()
        if prefix.find(" ") > 0:
            prefix = prefix[:prefix.find(" ")]  #remove string after all spaces
        while len(prefix) < count:
            prefix += '0'
        return prefix
        
    def name_get(self):
        res = super(res_partner,self).name_get()
        data = []
        for partner in self:
            name = ''
            if partner.ref:
                name += partner.ref
            name += ' ('
            name += partner.name
            name += ')'
            data.append((partner.id, name))
        return data
    
    @api.model
    def create(self, data):
        sequence = self.env['ir.sequence']
        if data['customer']:
            while True:
                prefix = self.get_prefix(data['name'])
                sequence = self.env['ir.sequence'].search([('prefix','=',prefix),('code','=','res.partner.account.code')])
                if not sequence:
                    padding = self.env.user.company_id.partner_ref_padding
                    implementation = 'no_gap'
                    active = True
                    sequence = self.env['ir.sequence'].create({'prefix':prefix,'padding':padding,'implementation':implementation,'active':active, 'name':'Account Code '+prefix,'code':'res.partner.account.code'})
                data['ref'] = sequence.next_by_id()
                if self.env['res.partner'].search([('ref','=',data['ref'])]):
                    _logger.debug('Account code exists')
                else:
                    break
        
        if data['supplier']:
            while True:
                prefix = 'O'
                sequence = self.env['ir.sequence'].search([('prefix','=',prefix),('code','=','res.partner.account.code')])
                if not sequence:
                    padding = 4
                    implementation = 'no_gap'
                    active = True
                    sequence = self.env['ir.sequence'].create({'prefix':prefix,'padding':padding,'implementation':implementation,'active':active, 'name':'Account Code '+prefix,'code':'res.partner.account.code'})
                data['ref'] = sequence.next_by_id()
                if self.env['res.partner'].search([('ref','=',data['ref'])]):
                    _logger.debug('Account code exists')
                else:
                    break
                    
        return super(res_partner, self).create(data)