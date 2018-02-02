# -*- coding: utf-8 -*-

from odoo import models, api, fields, _

class SalesRep(models.Model):
    _name = "sales.rep"    
    
    _order = "name asc"
    
    name = fields.Char('Sales Representative', required=True, translate=True)
    code = fields.Char('Code',required=True)
    phone = fields.Char(string="Phone #")
    active = fields.Boolean(default=True, help="If the active field is set to false, it will allow you to hide the sales rep without removing it.")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get('crm.team'))
    user_id = fields.Many2one('res.users', string='Team Leader')
    