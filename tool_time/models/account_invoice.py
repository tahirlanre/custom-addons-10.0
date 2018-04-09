from timer import timing

from odoo import models, api


class account_invoice(models.Model):
    _inherit = 'account.invoice'
    
    
class account_move(models.Model):
    _inherit = 'account.move'
    
    @timing
    @api.model
    def create(self, vals):
        return super(account_move,self).create(vals)
        
    