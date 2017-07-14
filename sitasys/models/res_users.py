# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID
from odoo import exceptions
from config import MAX
  
class ResUsers(models.Model):
    _inherit = "res.users"
    
    @api.model
    def create(self,vals):
        import pdb; pdb.set_trace()
        users = self.env['res.users'].search([])
        total_users = len(users)
        current_user = self.env.user
        new_total_users = total_users + 1
        if new_total_users > MAX and current_user.id != SUPERUSER_ID:
            raise exceptions.Warning('You have reached the maximum number of supported users! Please contact your Administrator')
        else:
            res = super(ResUsers,self).create(vals)
        return res
            
        