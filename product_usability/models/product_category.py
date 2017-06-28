# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError

class product_category(models.Model):
    _inherit = 'product.category'
    
    code = fields.Char(string="Category Code",default='[Auto]',required=True,unique=True)
    
    """def name_get(self):
        res = super(product_category,self).name_get()
        data = []
        for cat in self:
            name = ''
            if cat.code:
                name += cat.code
                name += ' '
            name += cat.name or ""
            data.append((cat.id,name))
        return data"""
            
    @api.model
    def create(self, vals):
        sequence_code = 'product.category'
        if vals.get('code', '[Auto]') == '[Auto]':
            while True:
                vals['code'] = self.env['ir.sequence'].next_by_code(sequence_code)
                if self.search([('code','=',vals['code'])]):
                    _logger.debug('Code must be unique')
                else:
                    break
                    
        if vals.get('code', '[Auto]') == '[Auto]':
            raise exceptions.ValidationError('No code defined!')
                    
        return super(product_category,self).create(vals)
        
    @api.constrains('code')
    def _check_code(self):
        for rec in self:
            if rec.code:
                list_cat_codes = self.search([('code','=',rec.code)])
                if list_cat_codes:
                    if len(list_cat_codes) == 1 and rec == list_cat_codes[0]:
                        return True
                    raise ValidationError('Category code must be unique!')
        return True