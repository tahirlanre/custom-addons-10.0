# -*- coding: utf-8 -*-
# © 2017 SITAYS (tahirlanre@hotmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields

class InventoryMovement(models.TransientModel):
    
    _name = 'report_inventory_movement_qweb'

    start_date = fields.Date("Start date")
    end_date = fields.Date("End date")
    summary = fields.Boolean()
    detailed = fields.Boolean()
    filter_product_ids = fields.Many2many(comodel_name='product.product')
    product_ids = fields.One2many(comodel_name='report_inventory_movement_product', inverse_name='report_id')
    line_ids = fields.One2many(comodel_name='report_inventory_movement_line', inverse_name='report_id')
    
    @api.multi
    def print_report(self, xlsx_report):
        self.ensure_one()
        self.compute_data_for_report()
        if xlsx_report:
            report_name='inventory_movement_report.inventory_movement_xlsx'
        else:
            report_name='inventory_movement_report.report_inventory_movement_qweb'

        return self.env['report'].get_action(report_name=report_name,docids=self.ids)

    @api.multi
    def compute_data_for_report(self):
        self.ensure_one()   

        self.inject_product_values()
        self.inject_line_values()
        
        
        self.refresh()
    
    def inject_line_values(self):
        
        query_inject_line_values="""
            INSERT INTO
                report_inventory_movement_line(
                    report_id,
                    create_uid,
                    create_date,
                    product_report_id,
                    date,
                    movement_type,
                    reference,
                    description,
                    qty_in,
                    qty_out,
                    picking_id,
                    move_id
                )
            SELECT
                    %s AS report_id,
                    %s AS create_uid,
                    NOW() AS create_date,
                    rp.id,
                    sh.date as date,
                    pit.name,
                    m.origin,
                    m.name,
                    case when sh.quantity > 0 THEN sh.quantity end as qty_in,
                    case when sh.quantity < 0 THEN sh.quantity * -1 end as qty_out,
                    pi.id,
                    m.id
                    from stock_history sh
                    left join stock_move m on m.id = sh.move_id
                    left join report_inventory_movement_product rp on rp.product_id = sh.product_id
                    left join stock_picking pi on pi.id = m.picking_id
                    left join stock_picking_type pit on pit.id = m.picking_type_id
                    where sh.date >= %s and sh.date <= %s    
        """
        if self.filter_product_ids:
            query_inject_line_values += """ and m.product_id in %s"""
        
        query_inject_line_values += """ order by date"""
          
        query_inject_parameters = (
            self.id,
            self.env.uid,
            self.start_date + ' 00:00:00',
            self.end_date + ' 23:59:59',
        )
        
        if self.filter_product_ids:
            query_inject_parameters += (tuple(self.filter_product_ids.ids),)
        
        self.env.cr.execute(query_inject_line_values, query_inject_parameters)
        
    def inject_product_values(self):
        query_inject_product_values ="""
            WITH line AS (SELECT
                        %s AS report_id,
                        %s AS create_uid,
                        NOW() AS create_date,
            			pp.id as product_id,
            			case when sh.quantity > 0 then sh.quantity else 0 end as qty_in,
            			case when sh.quantity < 0 then abs(sh.quantity) else 0 end as qty_out
            			from product_product pp
            			inner join stock_history sh on sh.product_id = pp.id
                        where sh.date >= %s and sh.date <= %s """
            
        if self.filter_product_ids:
            query_inject_product_values += """ and sh.product_id in %s"""
        
        query_inject_product_values += """
                        ),
        	opening_bal AS (SELECT SUM(h.quantity) as qty, h.product_id as product_id FROM stock_history h, 
        			stock_move m WHERE h.move_id=m.id and m.date < %s
        """
        
        if self.filter_product_ids:
            query_inject_product_values += """ and h.product_id in %s"""
            
        query_inject_product_values += """
    			   GROUP BY h.product_id),
    	     closing_bal AS (SELECT SUM(h.quantity) as qty, h.product_id as product_id FROM stock_history h, 
    			   stock_move m WHERE h.move_id=m.id and m.date <= %s
        """
        
        if self.filter_product_ids:
            query_inject_product_values += """ and h.product_id in %s"""
            
        query_inject_product_values += """
        			GROUP BY h.product_id
            )
            INSERT INTO 
                report_inventory_movement_product
                (
                    report_id,
                    create_uid,
                    create_date,
                    product_id,
                    code,
                    name,
                    opening_balance,
                    total_qty_in,
                    total_qty_out,
                    closing_balance
                )
            SELECT  
                    %s AS report_id,
                    %s AS create_uid,
                    NOW() as create_date,
        			l.product_id as product_id,
        			pt.default_code as code,
        			pt.name as product_name,
        			ob.qty as opening,
        			sum(l.qty_in) as total_in,
        			sum(l.qty_out) as total_out,
        			cb.qty as closing
        	FROM line l
        			left join product_product pp on pp.id = l.product_id
        			left join product_template pt on pt.id = pp.product_tmpl_id
        			left join opening_bal ob on ob.product_id = pp.id
        			left join closing_bal cb on cb.product_id = pp.id
            WHERE l.report_id = %s
            group by l.product_id, pt.default_code, pt.name, ob.qty, cb.qty
            ORDER BY code
            
        """   			
            			
        query_inject_parameters = (
            self.id,
            self.env.uid,
            self.start_date + ' 00:00:00',            
            self.end_date + ' 23:59:59',
        )
        
        if self.filter_product_ids:
            query_inject_parameters += (tuple(self.filter_product_ids.ids),)
        
        query_inject_parameters += (
            self.start_date + ' 00:00:00', 
        )
        
        if self.filter_product_ids:
            query_inject_parameters += (tuple(self.filter_product_ids.ids),)
            
        query_inject_parameters += (
            self.end_date + ' 23:59:59',
        )
        
        if self.filter_product_ids:
            query_inject_parameters += (tuple(self.filter_product_ids.ids),)
        
        query_inject_parameters += (
            self.id,
            self.env.uid,
            self.id,
        )
        
        self.env.cr.execute(query_inject_product_values, query_inject_parameters)
        
class InventoryMovementLine(models.TransientModel):
    _name = 'report_inventory_movement_line'
    
    date = fields.Date()
    movement_type = fields.Char()
    reference = fields.Char()
    description = fields.Char()
    qty_in = fields.Integer()
    qty_out = fields.Integer()
    picking_id = fields.Many2one('stock.picking', index=True)
    move_id = fields.Many2one('stock.move', index=True)
    report_id = fields.Many2one(comodel_name='report_inventory_movement_qweb', ondelete='cascade', index=True)
    product_report_id = fields.Many2one(comodel_name='report_inventory_movement_product', ondelete='cascade', index=True)
    
class InventoryMovementProduct(models.TransientModel):
    _name = 'report_inventory_movement_product'
    
    report_id = fields.Many2one(comodel_name='report_inventory_movement_qweb', ondelete='cascade', index=True)
    opening_balance = fields.Integer()
    closing_balance = fields.Integer()
    code = fields.Char()
    name = fields.Char()
    total_qty_in = fields.Integer()
    total_qty_out = fields.Integer()
    product_id = fields.Many2one('product.product', index=True)
    line_ids = fields.One2many(comodel_name='report_inventory_movement_line', inverse_name='product_report_id')
    
    