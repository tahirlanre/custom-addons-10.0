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
    
    summary = fields.Boolean()
    detailed = fields.Boolean()
    
    filter_product_ids = fields.Many2many(comodel_name='product.product')
    filter_partner_ids = fields.Many2many(comodel_name='res.partner')
    filter_sales_rep_ids = fields.Many2many(comodel_name='sales.rep')
    filter_product_category_ids = fields.Many2many(comodel_name='product.category')
    filter_transaction_types = fields.Many2many(comodel_name='inventory.transaction.type', relation='inventory_transaction_report_qweb_rel')
    #filter_in_invoice = fields.Boolean()
    #filter_out_invoice = fields.Boolean()
    #filter_in_refund = fields.Boolean()
    #filter_out_refund = fields.Boolean()
    
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
        
        if self.group_by_product:
            self.inject_product_values()
        
        elif self.group_by_partner:
            self.inject_partner_values()
        
        elif self.group_by_sales_rep:
            self.inject_sales_rep_values()
            
        self.inject_line_values()
        
        self.refresh()

    def inject_line_values(self):
        
        query_inject_line = """
            INSERT INTO
                report_inventory_transaction_line
                (
                    report_id,
           """
        if self.group_by_product:
            query_inject_line += """
                    product_report_id,
            """
        elif self.group_by_partner:
            query_inject_line += """
                    partner_report_id,
            """
        elif self.group_by_sales_rep:
            query_inject_line += """
                    sales_rep_report_id,
            """
        query_inject_line += """
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
                    invoice_name,
                    partner_code
                )
            SELECT
                    %s AS report_id,
            """
        if self.group_by_product:
            query_inject_line += """
                    rp.id AS product_report_id,
            """
        elif self.group_by_partner:
            query_inject_line += """
                    rpartner.partner_report_id,
            """
        elif self.group_by_sales_rep:
            query_inject_line += """
                    rs.sales_rep_report_id,
            """
        query_inject_line += """
                    %s AS create_uid,
                    NOW() AS create_date,
                    a.product_id, 
                    a.name, 
                    (invoice_type.sign * a.quantity) / u.factor * u2.factor AS product_qty,
                    (a.price_subtotal * invoice_type.sign) as amount,
	                a.purchase_price * (invoice_type.sign * a.quantity) / u.factor * u2.factor as total_cost,
	                invoice_type.sign * a.margin * invoice_type.sign as profit, 
                    invoice_type.sign * 100 * a.margin/NULLIF(a.price_subtotal,0) as percent_profit,
		            case when a.purchase_price = 0 then 0
		                else invoice_type.sign * 100 * a.margin/a.purchase_price end as markup,
        	        a.partner_id as partner_id,
                    pr.sales_rep_id,
                    i.date_invoice, i.number, pr.ref
                    from account_invoice_line a
                    left join account_invoice i on (i.id = a.invoice_id)
                    left join res_partner pr on (i.partner_id = pr.id)
                    LEFT JOIN product_product pp ON pp.id = a.product_id
                    left JOIN product_template pt ON pt.id = pp.product_tmpl_id
                    LEFT JOIN product_uom u ON u.id = a.uom_id
                    LEFT JOIN product_uom u2 ON u2.id = pt.uom_id
                    LEFT JOIN sales_rep sr on (pr.sales_rep_id = sr.id)
            """
        if self.group_by_product:
            query_inject_line += """
                    left join report_inventory_transaction_product rp on rp.product_id = a.product_id
            """
        elif self.group_by_partner:
            query_inject_line += """
                    left join report_inventory_transaction_partner rpartner on rpartner.partner_id = a.partner_id
            """
        elif self.group_by_sales_rep:
            query_inject_line += """
                    left join report_inventory_transaction_sales_rep rs on rs.sales_rep_id = pr.sales_rep_id
            """
        query_inject_line += """
                    JOIN (
                        -- Temporary table to decide if the qty should be added or retrieved (Invoice vs Refund) 
                        SELECT id,(CASE
                             WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text])
                                THEN -1
                                ELSE 1
                            END) AS sign
                        FROM account_invoice ai
                    ) AS invoice_type ON invoice_type.id = i.id
                    where i.state in ('paid', 'open') and i.date_invoice >= %s and i.date_invoice <= %s 
        """
        
        if self.filter_transaction_types:
            query_inject_line += """ and i.type in %s"""
        
        if self.filter_product_ids:
            query_inject_line += """ and a.product_id in %s"""
            
        if self.filter_partner_ids:
            query_inject_line += """ and a.partner_id in %s"""
            
        if self.filter_sales_rep_ids:
            query_inject_line += """ and pr.sales_rep_id in %s"""
            
        query_inject_line += """
                order by i.date_invoice asc
        """
            
        query_inject_parameters = (
            self.id,
            self.env.uid,
            self.start_date,
            self.end_date,
        )
        
        if self.filter_transaction_types:
            query_inject_parameters += (tuple(self.filter_transaction_types.mapped('type')),)
            
        if self.filter_product_ids:
            query_inject_parameters += (tuple(self.filter_product_ids.ids),)
        
        if self.filter_partner_ids:
            query_inject_parameters += (tuple(self.filter_partner_ids.ids),)
            
        if self.filter_sales_rep_ids:
            query_inject_parameters += (tuple(self.filter_sales_rep_ids.ids),)
            
        self.env.cr.execute(query_inject_line, query_inject_parameters)
    
    def inject_product_values(self):
        query_inject_product = """
            WITH line AS (
        		SELECT ail.id AS id,
        			ai.date_invoice AS date,
        			ail.product_id,
        			(ail.price_subtotal * invoice_type.sign) as amount,
        			(invoice_type.sign * ail.quantity) / u.factor * u2.factor AS product_qty,
        			ail.purchase_price * (invoice_type.sign * ail.quantity) / u.factor * u2.factor as total_cost,
        			invoice_type.sign * ail.margin as profit, 
        			invoice_type.sign * 100 * ail.margin/NULLIF(ail.price_subtotal,0) as percent_profit,
        			case when ail.purchase_price = 0 then 0
        	                else invoice_type.sign * 100 * ail.margin/ail.purchase_price end as markup,
                    ai.partner_id as partner_id,
                    partner.sales_rep_id
                        FROM account_invoice_line ail
                        JOIN account_invoice ai ON ai.id = ail.invoice_id
                        JOIN res_partner partner ON ai.commercial_partner_id = partner.id
                        LEFT JOIN product_product pr ON pr.id = ail.product_id
                        left JOIN product_template pt ON pt.id = pr.product_tmpl_id
                        LEFT JOIN product_uom u ON u.id = ail.uom_id
                        LEFT JOIN product_uom u2 ON u2.id = pt.uom_id
                        LEFT JOIN sales_rep sr on (partner.sales_rep_id = sr.id)
                        JOIN (
                            -- Temporary table to decide if the qty should be added or retrieved (Invoice vs Refund) 
                            SELECT id,(CASE
                                 WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text])
                                    THEN -1
                                    ELSE 1
                                END) AS sign
                            FROM account_invoice ai
                        ) AS invoice_type ON invoice_type.id = ai.id
                WHERE ai.state in ('paid', 'open') and ai.date >= %s and ai.date <= %s
            """
        if self.filter_transaction_types:
            query_inject_product += """ and ai.type in %s """
            
        if self.filter_product_ids:
            query_inject_product += """ and ail.product_id in %s"""
            
        if self.filter_partner_ids:
            query_inject_product += """ and a.partner_id in %s"""
            
        if self.filter_sales_rep_ids:
            query_inject_product += """ and partner.sales_rep_id in %s""" 
            
        query_inject_product += """
            ) 
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
                sum(rl.product_qty), sum(rl.amount), sum(rl.total_cost), 
                sum(rl.profit), 
                case when sum(rl.amount) = 0 then 0 
                    else 100 * sum(rl.profit)/sum(rl.amount) end, 
                case when sum(rl.total_cost) = 0 then 0 
                    else 100 * sum(rl.profit)/sum(rl.total_cost) end 
            FROM line rl
                left join product_product p on rl.product_id = p.id
                left join product_template pt on p.product_tmpl_id = pt.id
                group by rl.product_id, pt.default_code, pt.name
                order by pt.default_code asc
        """
        
        query_inject_parameters = (
            self.start_date,
            self.end_date,
        )
        
        if self.filter_transaction_types:
            query_inject_parameters += (tuple(self.filter_transaction_types.mapped('type')),)
             
        if self.filter_product_ids:
            query_inject_parameters += (tuple(self.filter_product_ids.ids),)
        
        if self.filter_partner_ids:
            query_inject_parameters += (tuple(self.filter_partner_ids.ids),)
        
        if self.filter_sales_rep_ids:
            query_inject_parameters += (tuple(self.filter_sales_rep_ids.ids),)
            
        query_inject_parameters += (
            self.id,
            self.env.uid,
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
    line_ids = fields.One2many(comodel_name='report_inventory_transaction_line', inverse_name='product_report_id')

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
    line_ids = fields.One2many(comodel_name='report_inventory_transaction_line', inverse_name='partner_report_id')
    
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
    partner_name = fields.Char()
    partner_code = fields.Char()
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
    product_report_id = fields.Many2one(comodel_name='report_inventory_transaction_product', ondelete='cascade', index=True)
    partner_report_id = fields.Many2one(comodel_name='report_inventory_transaction_partner', ondelete='cascade', index=True)
    
