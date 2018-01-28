# -*- coding: utf-8 -*-
# © 2018 SITAYS (sitasysnigeria@gmail.com)from odoo import api, models, fields, _
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _

class mda(models.Model):
    _name = 'document.mda'
    _order = 'code'
    
    code = fields.Char("Code", required=True, index=True)
    name = fields.Char("Name", required=True)
    
    @api.multi
    def name_get(self):
        res = super(mda,self).name_get()
        data = []
        for m_da in self:
            name = ''
            if m_da.code:
                name = m_da.code
            data.append((m_da.id, name))
        return data

class document_tax(models.Model):
    _name = 'document.tax'
    
    
    
class document_payment_voucher(models.Model):
    _name = 'document.payment.voucher'
    _order = 'payment_date'
    
    @api.multi
    @api.depends('gross_amount','tax_ids')
    def _compute_amount(self):
        for voucher in self:
            voucher.net_amount = voucher.gross_amount
        
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
    mda = fields.Many2one('document.mda', 'MDA',required=True)
    voucher_location = fields.Selection([('IL','IL')],required=True)
    voucher_no = fields.Integer(required=True)
    voucher_year = fields.Date(required=True)
    mda_fullname = fields.Char('Ministry/Department', related='mda.name')
    expenditure_type = fields.Selection([('capital','Capital'),('recurrent','Recurrent')],'Expenditure type', required=True)
    payment_mode = fields.Selection([('e_payment', 'E-Payment'),('cheque', 'Cheque')],'Payment mode', required=True)
    payment_reference = fields.Char('Payment reference')
    tax_ids = fields.Char('Tax')
    facevalue_document = fields.Binary('Face value', required=True)
    facevalue_document_filename = fields.Char('File name')
    releaseletter_document = fields.Binary('Release Letter', required=True)
    releaseletter_document_filename = fields.Char('File name')
    approvalletter_document = fields.Binary('Letter of Approval', required=True)
    approvalletter_document_filename = fields.Char('File name')
    govapproval_document = fields.Binary("Governor's Approval", required=True)
    govapproval_document_filename = fields.Char('File name')
    vat_document = fields.Binary('VAT document')
    vat_document_filename = fields.Char('File name')
    wht_document = fields.Binary('Witholding tax document')
    wht_document_filename = fields.Char('File name')
    dl_document = fields.Binary('Development levy document')
    dl_document_filename = fields.Char('File name')
    sd_document = fields.Binary('Stamp duty document')
    sd_document_filename = fields.Char('File name')
    other_document = fields.Binary('Other document')
    other_document_filename = fields.Char('File name')
    
    @api.model
    def create(self,vals):
        if not vals.get('dept_no'):
            code = self.env['document.mda'].browse(vals['mda']).code
            voucher_location = vals['voucher_location']
            voucher_no = vals['voucher_no']
            voucher_year = vals['voucher_year'].split('-')[0]
            vals['dept_no']=str(code)+'/'+str(voucher_location)+'/'+str(voucher_no)+'/'+str(voucher_year)
        return super(document_payment_voucher,self).create(vals)
            
    @api.multi
    def unlink(self):
        #TODO - implement unlink funciton
        pass
    
class document_release_letter(models.Model):
    _name = 'document.release.letter'
    
    reference = fields.Char('Reference No', required=True)
    date = fields.Date('Date', required=True)
    mda = fields.Many2one('document.mda',string='Ministry/Department', required=True)
    gross_amount = fields.Float('Gross Amount', required=True)
    releaseletter_document = fields.Binary('Release Letter', required=True)
    releaseletter_document_filename = fields.Char('File name')
    

    