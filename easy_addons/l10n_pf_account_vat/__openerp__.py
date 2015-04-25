# -*- coding: utf-8 -*-
{
    'name': "Déclaration de TVA - PF",

    'summary': """
        Account, VAT, French Polynesia""",

    'description': """
		Ce module permet d'automatiser les déclarations de TVA
		de la Polynésie Française.
		TODO:
		- Dispatcher les saisies des comptes
		- MultiSociétés

    """,

    'author': "EasyPME",
    'website': "http://www.easypme.com",

    'category': 'Account',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'l10n_pf'],

    # always loaded
    'data': [
		#'security/l10n_pf_account_vat_security.xml',
        'security/ir.model.access.csv',
        'wizard/l10n_pf_account_vat_journal_items_view.xml',
        'views/l10n_pf_account_vat_view.xml',
        'views/res_company_view.xml',
        'views/account_move_line_view.xml',
        'report/l10n_pf_account_vat_report.xml',
        'report/l10n_pf_account_vat_report_declaration.xml',
        'report/report_deposit_l10n_pf_account_vat.xml',
        'report/report_annual_l10n_pf_account_vat.xml',
        'report/report_real_l10n_pf_account_vat.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
