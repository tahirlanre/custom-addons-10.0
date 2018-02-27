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
    
class document_payment_voucher(models.Model):
    _name = 'document.payment.voucher'
    _order = 'payment_date'
    
    @api.multi
    @api.depends('gross_amount','tax_ids')
    def _compute_amount(self):
        for voucher in self:
            taxes = False
            total_tax = 0.0
            if voucher.tax_ids:
                taxes = voucher.tax_ids
                for tax in voucher.tax_ids:
                    if tax.amount_type == 'percent':
                        tax_amount = voucher.gross_amount * tax.amount / 100
                        total_tax = total_tax + tax_amount
            voucher.net_amount = (voucher.gross_amount - total_tax) if taxes else voucher.gross_amount
        
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
    tax_ids = fields.Many2many('document.payment.voucher.tax',string='Taxes')
    facevalue_document = fields.Binary('Face value', required=True)
    facevalue_document_filename = fields.Char('File name')
    releaseletter_document = fields.Binary('Release Letter')
    releaseletter_document_filename = fields.Char('File name')
    approvalletter_document = fields.Binary('Letter of Approval')
    approvalletter_document_filename = fields.Char('File name')
    govapproval_document = fields.Binary("Governor's Approval")
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
    

class document_payment_voucher_tax(models.Model):
    _name = 'document.payment.voucher.tax'
    
    name = fields.Char(string='Tax Name', required=True, translate=True)
    amount_type = fields.Selection(default='percent', string="Tax Computation", required=True, oldname='type',
        selection=[('group', 'Group of Taxes'), ('fixed', 'Fixed'), ('percent', 'Percentage')])
    active = fields.Boolean(default=True, help="Set active to false to hide the tax without removing it.")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    sequence = fields.Integer(required=True, default=1,
        help="The sequence field is used to define order in which the tax lines are applied.")
    amount = fields.Float(required=True, digits=(16, 4))
    description = fields.Char(string='Label on Payment Voucher', translate=True)
    price_include = fields.Boolean(string='Included in Price', default=False,
        help="Check this if the price you use on the product and invoices includes this tax.")
    include_base_amount = fields.Boolean(string='Affect Base of Subsequent Taxes', default=False,
        help="If set, taxes which are computed after this one will be computed based on the price tax included.")
    analytic = fields.Boolean(string="Include in Analytic Cost", help="If set, the amount computed by this tax will be assigned to the same analytic account as the invoice line (if any)")

    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id)', 'Tax names must be unique !'),
    ]