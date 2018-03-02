# -*- coding: utf-8 -*-
# © 2017 SITAYS (tahirlanre@hotmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields

class inventory_transaction(models.TransientModel):
    
    _name = 'report_inventory_transaction_qweb'

    start_date = fields.Date("Start date")
    end_date = fields.Date("End date")
    group_by_product = fields.Boolean()
    group_by_sales_rep = fields.Boolean()
    group_by_partner = fields.Boolean()
    filter_product_ids = fields.Many2many(comodel_name='product.product')
    filter_partner_ids = fields.Many2many(comodel_name='res.partner')
    filter_sales_rep_ids = fields.Many2many(comodel_name='sales.rep')

    product_ids = fields.One2many(comodel_name='report_inventory_transaction_product', inverse_name='report_id')
    line_ids = fields.One2many(comodel_name='report_inventory_transaction_line', inverse_name='report_id')
    partner_ids = fields.One2many(comodel_name='report_inventory_transaction_partner', inverse_name='report_id')
    sales_rep_ids = fields.One2many(comodel_name='report_inventory_transaction_sales_rep', inverse_name='report_id')

    @api.multi
    def print_report(self, xlsx_report):
        self.ensure_one()
        self.compute_data_for_report()
        if xlsx_report:
            report_name='inventory_transaction.inventory_transaction_xlsx'
        else:
            report_name='inventory_transaction.report_inventory_transaction_qweb'

        return self.env['report'].get_action(report_name=report_name,docids=self.ids)

    @api.multi
    def compute_data_for_report(self):
        self.ensure_one()
        self.inject_line_values()
        
        if self.group_by_product:
            self.inject_product_values()
        
        if self.group_by_partner:
            self.inject_partner_values()
        
        if self.group_by_sales_rep:
            self.inject_sales_rep_values()
        
        self.refresh()

    def inject_line_values(self):
        
        query_inject_line = """
            INSERT INTO
                report_inventory_transaction_line
                (
                    report_id,
                    create_uid,
                    create_date,
                    product_id,
                    name,
                    qty,
                    amount,
                    cost,
                    profit,
                    percent_profit,
                    percent_markup,
                    partner_id,
                    sales_rep_id,
                    date,
                    invoice_name
                )
            SELECT
                    %s AS report_id,
                    %s AS create_uid,
                    NOW() AS create_date,
                    a.product_id, a.name, a.quantity as qty, a.price_subtotal as amount,
	                a.purchase_price * a.quantity as total_cost,
	                a.margin as profit, 100 * a.margin/NULLIF(a.price_subtotal,0) as percent_profit,
		            case when a.purchase_price = 0 then 0
		                else 100 * a.margin/a.purchase_price end as markup,
        	        a.partner_id as partner_id,
                    pr.sales_rep_id,
                    i.date_invoice, i.number
                    from account_invoice_line a
                    left join account_invoice i on (i.id = a.invoice_id)
                    left join res_partner pr on (i.partner_id = pr.id)
                    left join sales_rep sr on (pr.sales_rep_id = sr.id )
                    where i.date_invoice >= %s and i.date_invoice <= %s and i.type in ('out_invoice') and i.state in ('paid', 'open')
        """
        if self.filter_product_ids:
            query_inject_line += """ and a.product_id in %s"""
            
        if self.filter_partner_ids:
            query_inject_line += """ and a.partner_id in %s"""
            
        if self.filter_sales_rep_ids:
            query_inject_line += """ and pr.sales_rep_id in %s"""
            
        query_inject_parameters = (
            self.id,
            self.env.uid,
            self.start_date,
            self.end_date,
        )
        
        if self.filter_product_ids:
            query_inject_parameters += (tuple(self.filter_product_ids.ids),)
        
        if self.filter_partner_ids:
            query_inject_parameters += (tuple(self.filter_partner_ids.ids),)
            
        if self.filter_sales_rep_ids:
            query_inject_parameters += (tuple(self.filter_sales_rep_ids.ids),)
         
        query_inject_line += """
            UNION ALL
            SELECT	
                    %s AS report_id,
                    %s AS create_uid,
                    NOW() AS create_date,
                    a.product_id, a.name, a.quantity * -1 as qty, a.price_subtotal * -1 as amount,
            	    a.purchase_price * a.quantity * -1 as total_cost,
                	a.margin * -1 as profit, 100 * a.margin/NULLIF(a.price_subtotal,0) as percent_profit,
                    case when a.purchase_price = 0 then 0
                		else 100 * a.margin/a.purchase_price end as markup,
                	a.partner_id as partner_id,
                	pr.sales_rep_id,
                	i.date_invoice, i.number
                	from account_invoice_line a
                	left join account_invoice i on (i.id = a.invoice_id)
                	left join res_partner pr on (i.partner_id = pr.id)
                	left join sales_rep sr on (pr.sales_rep_id = sr.id )
                	where i.date_invoice >= %s and i.date_invoice <= %s and i.type in ('out_refund') and i.state in ('paid', 'open')
        """
        
        if self.filter_product_ids:
            query_inject_line += """ and a.product_id in %s"""
            
        if self.filter_partner_ids:
            query_inject_line += """ and a.partner_id in %s"""
            
        if self.filter_sales_rep_ids:
            query_inject_line += """ and pr.sales_rep_id in %s"""
                    
        query_inject_parameters += (
            self.id,
            self.env.uid,
            self.start_date,
            self.end_date,
        )
        
        if self.filter_product_ids:
            query_inject_parameters += (tuple(self.filter_product_ids.ids),)
        
        if self.filter_partner_ids:
            query_inject_parameters += (tuple(self.filter_partner_ids.ids),)
        
        if self.filter_sales_rep_ids:
            query_inject_parameters += (tuple(self.filter_sales_rep_ids.ids),)
            
        self.env.cr.execute(query_inject_line, query_inject_parameters)
    
    def inject_product_values(self):
        query_inject_product = """
            INSERT INTO
                report_inventory_transaction_product
                (
                    report_id,
                    create_uid,
                    create_date,
                    product_id,
                    code,
                    name,
                    qty,
                    amount,
                    cost,
                    profit,
                    percent_profit,
                    percent_markup
                )
            SELECT
                %s AS report_id,
                %s AS create_uid,
                NOW() as create_date,
                rl.product_id, pt.default_code, pt.name, 
                sum(rl.qty), sum(rl.amount), sum(rl.cost), 
                sum(rl.profit), 
                case when sum(rl.amount) = 0 then 0 
                    else 100 * sum(rl.profit)/sum(rl.amount) end, 
                case when sum(rl.cost) = 0 then 0 
                    else 100 * sum(rl.profit)/sum(rl.cost) end from
                report_inventory_transaction_line rl
                left join product_product p on rl.product_id = p.id
                left join product_template pt on p.product_tmpl_id = pt.id
                where rl.report_id = %s
                group by rl.product_id, pt.default_code, pt.name
                order by pt.default_code asc
        """
        
        query_inject_parameters = (
            self.id,
            self.env.uid,
            self.id,
        )
        self.env.cr.execute(query_inject_product, query_inject_parameters)
        
    def inject_partner_values(self):
        query_inject_partner = """
            INSERT INTO
                report_inventory_transaction_partner
                (
                    report_id,
                    create_uid,
                    create_date,
                    partner_id,
                    code,
                    name,
                    qty,
                    amount,
                    cost,
                    profit,
                    percent_profit,
                    percent_markup
                )
            SELECT
                %s AS report_id,
                %s AS create_uid,
                NOW() as create_date,
                rl.partner_id, p.ref, p.name, 
                sum(rl.qty), sum(rl.amount), sum(rl.cost), 
                sum(rl.profit),
                case when sum(rl.amount) = 0 then 0 
                    else 100 * sum(rl.profit)/sum(rl.amount) end, 
                case when sum(rl.cost) = 0 then 0 
                    else 100 * sum(rl.profit)/sum(rl.cost) end from
                report_inventory_transaction_line rl
                join res_partner p on rl.partner_id = p.id
                where rl.report_id = %s
                group by rl.partner_id, p.ref, p.name
                order by p.ref asc
        """
        
        query_inject_parameters = (
            self.id,
            self.env.uid,
            self.id,
        )
        self.env.cr.execute(query_inject_partner, query_inject_parameters)
    
    def inject_sales_rep_values(self):
        query_inject_sales_rep = """
            INSERT INTO
                report_inventory_transaction_sales_rep
                (
                    report_id,
                    create_uid,
                    create_date,
                    sales_rep_id,
                    name,
                    qty,
                    amount,
                    cost,
                    profit,
                    percent_profit,
                    percent_markup
                )
            SELECT
                %s AS report_id,
                %s AS create_uid,
                NOW() as create_date,
                rl.sales_rep_id, sr.name, 
                sum(rl.qty), sum(rl.amount), sum(rl.cost), 
                sum(rl.profit), 
                case when sum(rl.amount) = 0 then 0 
                    else 100 * sum(rl.profit)/sum(rl.amount) end, 
                case when sum(rl.cost) = 0 then 0 
                    else 100 * sum(rl.profit)/sum(rl.cost) end from
                report_inventory_transaction_line rl
                join sales_rep sr on rl.sales_rep_id = sr.id
                where rl.report_id = %s
                group by rl.sales_rep_id, sr.name
                order by sr.name asc
        """
        
        query_inject_parameters = (
            self.id,
            self.env.uid,
            self.id,
        )
        self.env.cr.execute(query_inject_sales_rep, query_inject_parameters)
        
class InventorySalesAnalysisProduct(models.TransientModel):
    _name = 'report_inventory_transaction_product'

    code = fields.Char()
    name = fields.Char()
    qty = fields.Float()
    amount = fields.Float()
    cost = fields.Float()
    profit = fields.Float()
    percent_profit = fields.Float()
    percent_markup = fields.Float()
    product_id = fields.Many2one('product.product', index = True)
    report_id = fields.Many2one(comodel_name='report_inventory_transaction_qweb', ondelete='cascade', index=True)

class InventorySalesAnalysisPartner(models.TransientModel):
    _name = 'report_inventory_transaction_partner'
    
    code = fields.Char()
    name = fields.Char()
    qty = fields.Float()
    amount = fields.Float()
    cost = fields.Float()
    profit = fields.Float()
    percent_profit = fields.Float()
    percent_markup = fields.Float()
    partner_id = fields.Many2one('res.partner', index = True)
    report_id = fields.Many2one(comodel_name='report_inventory_transaction_qweb', ondelete='cascade', index=True)
    
class InventorySalesAnalysisSalesRep(models.TransientModel):
    _name = 'report_inventory_transaction_sales_rep'
    
    #code = fields.Char()
    name = fields.Char()
    qty = fields.Float()
    amount = fields.Float()
    cost = fields.Float()
    profit = fields.Float()
    percent_profit = fields.Float()
    percent_markup = fields.Float()
    sales_rep_id = fields.Many2one('sales.rep', index = True)
    report_id = fields.Many2one(comodel_name='report_inventory_transaction_qweb', ondelete='cascade', index=True)

class InventorySalesAnalysisLine(models.TransientModel):
    _name = 'report_inventory_transaction_line'

    product_id = fields.Many2one('product.product', index = True)
    partner_id = fields.Many2one('res.partner', index = True)
    sales_rep_id = fields.Many2one('sales.rep', index = True)
    invoice_name = fields.Char()
    #code = fields.Char()
    name = fields.Char()
    qty = fields.Float()
    amount = fields.Float()
    cost = fields.Float()
    profit = fields.Float()
    percent_profit = fields.Float()
    percent_markup = fields.Float()
    date = fields.Date()

    report_id = fields.Many2one(comodel_name='report_inventory_transaction_qweb', ondelete='cascade', index = True)
