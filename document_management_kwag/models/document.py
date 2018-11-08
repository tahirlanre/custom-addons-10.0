# -*- coding: utf-8 -*-
# © 2018 SITAYS (sitasysnigeria@gmail.com)from odoo import api, models, fields, _
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.tools import amount_to_text_en
from odoo.osv import expression

class mda(models.Model):
    _name = 'document.mda'
    _order = 'code'
    
    code = fields.Char("Code", required=True, index=True)
    name = fields.Char("Name", required=True)
    economic_code = fields.Char("Economic Code")
    
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
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        mdas = self.search(domain + args, limit=limit)
        return mdas.name_get()
        
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
    
    @api.multi
    @api.depends('voucher_location','voucher_no','voucher_year')
    def _set_dept_no(self):
        for voucher in self:
            if voucher.voucher_location and voucher.voucher_no and voucher.voucher_year and voucher.mda:
                code = voucher.mda.code
                voucher_location = voucher.voucher_location
                voucher_no = voucher.voucher_no
                voucher_year = voucher.voucher_year.split('-')[0]
                voucher.dept_no = str(code)+'/'+str(voucher_location)+'/'+str(voucher_no)+'/'+str(voucher_year)
            
    @api.multi
    @api.depends('net_amount')    
    def _amount_to_text(self,):
        for voucher in self:
            convert_amount_in_words = amount_to_text_en.amount_to_text(voucher.net_amount, lang='en', currency='Naira')        
            convert_amount_in_words = convert_amount_in_words.replace(' Cents', ' Kobo ')
            convert_amount_in_words = convert_amount_in_words.replace(' Cent', ' Kobo ')
            convert_amount_in_words = convert_amount_in_words.replace(' and Zero Kobo', ' Only')
            voucher.net_amount_text = convert_amount_in_words
    
    @api.multi
    @api.onchange('sub_code')
    def _set_sub_sub_code(self):
        for voucher in self:
            voucher.sub_sub_code = voucher.sub_code
            
    parent_id = fields.Many2one('document.payment.voucher', "Parent", ondelete="cascade", index=True)
    payment_date = fields.Date('Payment Date', required=True)
    payment_account = fields.Many2one('document.payment.voucher.account',string='Payment Account', required=True)
    description = fields.Text('Description')
    dept_no = fields.Char('Department No', compute='_set_dept_no', store=True)
    partner_id = fields.Many2one('res.partner', string='Payee', required=True)
    gross_amount = fields.Float('Gross Amount', required=True)
    net_amount = fields.Float('Net Amount', compute='_compute_amount')
    child_vat = fields.One2many('document.payment.voucher', 'parent_id', string='VAT')
    child_wht = fields.One2many('document.payment.voucher', 'parent_id', string='Witholding Tax')
    child_dl = fields.One2many('document.payment.voucher', 'parent_id', string='Development Levy')
    child_sd = fields.One2many('document.payment.voucher', 'parent_id', string='Standing Order')
    mda = fields.Many2one('document.mda', 'MDA',required=True)
    voucher_location = fields.Char(required=True)
    voucher_no = fields.Integer(required=True)
    voucher_year = fields.Date(required=True)
    mda_fullname = fields.Char('Ministry/Department', related='mda.name')
    expenditure_type = fields.Selection([('capital','Capital'),('recurrent','Recurrent')],'Expenditure type', required=True)
    payment_mode = fields.Selection([('e_payment', 'E-Payment'),('cheque', 'Cheque')],'Payment mode', required=True)
    payment_reference = fields.Char('Payment reference')
    tax_ids = fields.Many2many('document.payment.voucher.tax',string='Taxes')
    facevalue_document = fields.Binary('Face value')
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
    doc_attachment_id = fields.Many2many('ir.attachment', 'doc_attach_rel', 'doc_id', 'attach_id3', string="Document attachment",
                                         help='You can attach the copy of your document', copy=False, required=True)
    net_amount_text = fields.Char('Net amount in words', compute='_amount_to_text')
    release_letter_ref_no = fields.Char('Release letter ref no')
    code = fields.Char('Code', related='mda.economic_code')
    sub_code = fields.Char('Sub-code', required=True)
    sub_sub_code = fields.Char('Sub Sub-code')
    
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
    def name_get(self):
        res = super(document_payment_voucher,self).name_get()
        data = []
        for voucher in self:
            name = ''
            if voucher.dept_no:
                name = voucher.dept_no
            data.append((voucher.id, name))
        return data
    
class document_release_letter(models.Model):
    _name = 'document.release.letter'
    
    @api.multi
    @api.depends('gross_amount')    
    def _amount_to_text(self,):
        for release_letter in self:
            convert_amount_in_words = amount_to_text_en.amount_to_text(release_letter.gross_amount, lang='en', currency='Naira')        
            convert_amount_in_words = convert_amount_in_words.replace(' Cents', ' Kobo ')
            convert_amount_in_words = convert_amount_in_words.replace(' Cent', ' Kobo ')
            convert_amount_in_words = convert_amount_in_words.replace(' and Zero Kobo', ' Only')
            release_letter.gross_amount_text = convert_amount_in_words
    
    reference = fields.Char('Reference No', required=True)
    date = fields.Date('Date', required=True)
    mda = fields.Many2one('document.mda',string='Ministry/Department', required=True)
    gross_amount = fields.Float('Gross Amount', required=True)
    gross_amount_text = fields.Char('Net amount in words', compute='_amount_to_text')
    doc_attachment_id = fields.Many2many('ir.attachment', 'doc_attach_rel', 'doc_id', 'attach_id3', string="Document attachment",
                                         help='You can attach the copy of your document', copy=False, required=True)
    releaseletter_document = fields.Binary('Release Letter')
    releaseletter_document_filename = fields.Char('File name')
    releaseletter_range = fields.Char('Release letter range')
    
    @api.multi
    def name_get(self):
        res = super(document_release_letter,self).name_get()
        data = []
        for release_letter in self:
            name = ''
            if release_letter.reference:
                name = release_letter.reference
            data.append((release_letter.id, name))
        return data
    

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

class document_payment_voucher_account(models.Model):
    _name = 'document.payment.voucher.account'
    
    name = fields.Char(string='Account name', required=True)
    bank = fields.Char(string='Bank', required=True)
    account_no = fields.Char('Account No')
    
    @api.multi
    def name_get(self):
        res = super(document_payment_voucher_account,self).name_get()
        data = []
        for account in self:
            name = ''
            if account.bank:
                name = account.name + ' - ' + account.bank
            data.append((account.id, name))
        return data
        
        
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('bank', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        accounts = self.search(domain + args, limit=limit)
        return accounts.name_get()