# -*- coding: utf-8 -*-
# © 2018 SITAYS (sitasysnigeria@gmail.com)from odoo import api, models, fields, _
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _

class mda(models.Model):
    _name = 'document.mda'
    _order = 'code'
    
    name = fields.Char("Name", required=True, index=True)
    code = fields.Char("Code", required=True)

class document_payment_voucher(models.Model):
    _name = 'document.payment.voucher'
    _order = 'payment_date'
    
    @api.depends('gross_amount','tax_ids')
    def _compute_amount(self):
        pass
        
    parent_id = fields.Many2one('document.payment.voucher', "Parent", ondelete="cascade", index=True)
    payment_date = fields.Date('Payment Date', required=True)
    payment_account = fields.Char('Payment Account', required=True)
    description = fields.Char('Description')
    dept_no = fields.Char('Department No', required=True)
    partner_id = fields.Many2one('res.partner', string='Payee', required=True)
    gross_amount = fields.Float('Gross Amount', required=True)
    net_amount = fields.Float('Net Amount', compute='_compute_amount')
    child_vat = fields.One2many('document.payment.voucher', 'parent_id', string='VAT')
    child_wht = fields.One2many('document.payment.voucher', 'parent_id', string='Witholding Tax')
    child_dl = fields.One2many('document.payment.voucher', 'parent_id', string='Development Levy')
    child_sd = fields.One2many('document.payment.voucher', 'parent_id', string='Standing Order')
    mda = fields.Many2one('document.mda',string='Ministry/Department', required=True)
    expenditure_type = fields.Selection([('capital','Capital'),('recurrent','Recurrent')],'Expenditure type', required=True)
    payment_mode = fields.Selection([('e_payment', 'E-Payment'),('cheque', 'Cheque')],'Payment mode', required=True)
    payment_reference = fields.Char('Payment reference')
    tax_ids = fields.Char('Tax')
    
class document_release_letter(models.Model):
    _name = 'document.release.letter'
    
    reference = fields.Char('Reference No', required=True)
    date = fields.Date('Date', required=True)
    mda = fields.Many2one('document.mda',string='Ministry/Department', required=True)
    gross_amount = fields.Float('Gross Amount', required=True)
    

    