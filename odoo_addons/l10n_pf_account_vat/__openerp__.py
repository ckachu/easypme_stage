# -*- coding: utf-8 -*-
{
    'name': "Déclaration de TVA - PF",

    'summary': """
        Account, VAT, French Polynesia""",

    'description': """
		Ce module permet d'automatiser les déclarations de TVA 
		de la Polynésie Française.
    """,

    'author': "EasyPME",
    'website': "http://www.easypme.com",

    'category': 'Account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'l10n_pf_account_vat_view.xml',
        'res_company_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
