{
    'name': 'Sales Rep Commission',
    'author': 'Tahir Aduragba',
    'data': [
         'security/ir.model.access.csv',
         'views/sales_rep_commission_view.xml',
         'views/sales_rep_commission_menu.xml',
         'views/product_template_view.xml',
         'wizard/sales_rep_commission_wizard.xml',
         'report/templates/sales_rep_commission_report.xml',
         'reports.xml',
     ],
    'depends': ['sale', 'partner_sales_rep','account'],
    'application': True
}
