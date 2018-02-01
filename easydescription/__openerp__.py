{
    'name': 'Easy Description',
    'version': '1.0',
    'author': 'Awtol',
    'category': 'Sales',
    'website': 'https://awtol.com',
    'description': """
Permit to have HTMK Description on Sales and Invoices
======================
""",
    'depends': ['base','sale','account'],
    'data': ['easydescription_view.xml', 
             'security/ir.model.access.csv', ],
    'active': True,
    'installable': True,
    'auto_install': False,
}
