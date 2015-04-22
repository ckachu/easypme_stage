# -*- coding: utf-8 -*-
{
    'name': "Varua Crewz Profile",

    'description': """
    Module destiné à Varua Crewz
    """,

    'author': "EasyPME",
    'website': "http://www.easypme.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Website',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/varuacrewz_profile_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
