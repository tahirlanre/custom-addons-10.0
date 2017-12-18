# -*- coding: utf-8 -*-
# © 2017 SITAYS (tahirlanre@hotmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields

class InventoryMovement(models.TransientModel):
    
    _name = 'report_inventory_movement_qweb'

    start_date = fields.Date("Start date")
    end_date = fields.Date("End date")
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
                    pr.id,
                    sh.date,
                    pit.name,
                    m.name,
                    pi.name,
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
            query_inject_line += """ and m.product_id in %s"""
            
        query_inject_parameters = (
            self.id,
            self.env.uid,
            self.start_date,
            self.end_date,
        )
        
        if self.filter_product_ids:
            query_inject_parameters += (tuple(self.filter_product_ids.ids),)
        
        self.env.cr.execute(query_inject_line, query_inject_parameters)
        
    def inject_product_values(self):
        query_inject_product_values ="""
            WITH 
                lines AS (
                    SELECT
                        pr.id,
                        sh.date,
                        pit.name,
                        m.name,
                        pi.name,
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
            query_inject_product_values += """ and m.product_id in %s"""
            
        query_inject_product_values += """
                )
            INSERT INTO
                report_inventory_movement_product(
                    report_id,
                    create_uid,
                    create_date,
                    opening_balance,
                    closing_balance,
                    code,
                    name,
                    total_qty_in,
                    total_qty_out,
                    product_id
                )
            SELECT 
                %s AS report_id,
                %s AS create_uid,
                NOW() as create_date,
                ob.qty,
                oc.qty,
                pt.code,
                pt.name,
                in.qty,
                out.qty,
                sh.product_id
                from stock_history sh
                left join product_product pp on pp.id = sh.product_id
                left join product_template pt on pt.id = pp.id
                left join (SELECT SUM(h.quantity) as qty, h.product_id as product_id FROM stock_history h, 
                                stock_move m WHERE h.move_id=m.id AND h.product_id = pp.id 
                                AND m.date < %s GROUP BY h.product_id) as ob on ob.product_id = pp.id,
                left join (SELECT SUM(h.quantity) as qty, h.product_id as product_id FROM stock_history h, 
                                stock_move m WHERE h.move_id=m.id AND h.product_id = pp.id 
                                AND m.date < %s GROUP BY h.product_id) as ob) as oc on oc.product_id = pp.id,
                left join (SELECT SUM(h.quantity) as qty, h.product_id as product_id
                                FROM stock_history h, stock_move m
                                WHERE h.move_id=m.id AND 
                                h.product_id=pp.id AND h.quantity > 0 AND 
                                m.date >= %s AND m.date <= %s 
                                GROUP BY h.product_id) as in on in.product_id
                left join (SELECT SUM(h.quantity) as qty, h.product_id as product_id
                                FROM stock_history h, stock_move m
                                WHERE h.move_id=m.id AND 
                                h.product_id=pp.id AND h.quantity < 0 AND 
                                m.date >= %s AND m.date <= %s 
                                GROUP BY h.product_id) as out on out.product_id
                
        
        """
        
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
    product_report_id = fields.Many2one(comodel_name='report_inventory_movement_qweb', ondelete='cascade', index=True)
    
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
    
    