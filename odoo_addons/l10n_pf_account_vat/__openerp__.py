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
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/l10n_pf_account_vat_view.xml',
        'views/res_company_view.xml',
        'l10n_pf_account_vat_report.xml',
        'report_deposit_l10n_pf_account_vat.xml',
        'report_annual_l10n_pf_account_vat.xml',
        'report_real_l10n_pf_account_vat.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
