# -*- coding: utf-8 -*-
{
    'name': "sales_leads_easypme",

    'summary': """
        No summary""",

    'description': """
        Ajoute le champ Vendeur à la vue List des Pistes
    """,

    'author': "EasyPME",
    'website': "http://www.easypme.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['crm'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'sales_leads_easypme_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
