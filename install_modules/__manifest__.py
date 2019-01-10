# -*- coding: utf-8 -*-
{
    'name': "Install Modules Immediately",

    'summary': """
        Installs required modules on Odoo 10
        """,

    'description': """
        
    """,

    'author': "SITASYS",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','ar_transaction','account_bank_statement_import','account_cashbook_batch','account_limit','account_fiscal_year','account_invoice_margin','account_move_import','account_type_inactive','account_type_menu','account_accountant','houseaffairs_account_usability','analytic','asset_usability','account_asset','barcodes','base','web_kanban','base_import','report_xlsx','account_cancel','account_invoice_refund_option','houseaffairs_account_financial_report','account_financial_report_qweb_custom','custom_partner_ref_generator','houseaffairs_custom_so_report','customer_vendor_statement','custom_auto_backup','date_range','decimal_precision','deltatech','deltatech_stock_date','deltatech_stock_inventory','mail','fetchmail','web_kanban_gauge','account_general_ledger_enquiry','l10n_generic_coa','hide_update_qty_button','houseaffairs_access_control','bus','base_setup','stock','inventory_movement_report','inventory_sales_analysis','inventory_transaction','inventory_valuation','houseaffairs_custom_invoice','account','account_journal_batch','procurement_jit','product_margin_category','product_margin','mass_editing','web_settings_dashboard','web_diagram','account_partner_balance','partner_sales_rep','auth_crypt','payment','payment_usability','web_planner','portal','portal_sale','portal_stock','procurement','product_usability','product','purchase_auto_invoice','purchase','purchase_usability','account_financial_report_qweb','web_readonly_bypass','report','report_qweb_element_page_visibility','sitasys','sale_auto_process','sale','sales_rep_commission','sales_team','sale_usability','sale_stock','auth_signup','account_standard_report','stock_picking_invoice_link','stock_usability','tax_invoice_report','web_tour','payment_transfer','stock_account','web','web_calendar','web_editor','web_export_view','web_no_bubble','web_pdf_preview','web_widget_color','report_extended'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}