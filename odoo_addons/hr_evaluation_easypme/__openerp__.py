# -*- coding: utf-8 -*-
{
    'name': "EasyPME Profiles",
    'version': '0.1',
    'author': 'EasyPME',
    'category': 'Human Resources',
    'summary': """Access Rights, Profiles, Evaluation""",

    'description': """Define access rights for EasyPME profiles""",

    'author': "EasyPME",
    'website': "http://www.yourcompany.com",

    # any module necessary for this one to work correctly
    'depends': ['hr_evaluation'],

    # always loaded
    'data': [
		'security/hr_evaluation_easypme_security.xml',
        'security/ir.model.access.csv'
    ],
    # only loaded in demonstration mode
    'demo': [
        #'l10n_pf_hr_evaluation_easypme_demo.xml',
    ],
}

