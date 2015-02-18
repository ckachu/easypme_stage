# -*- coding: utf-8 -*-
{
    'name': "hr_evaluation_polymtl",

    'summary': """
        Evaluation Polymtl mi-intership""",

    'description': """
    """,

    'author': "EasyPME",
    'website': "http://www.easypme.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'RH Evaluation',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_evaluation'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
	'survey_data_appraisal_polymtl.xml',
	'hr_evaluation_polymtl_data.xml'   
],
    # only loaded in demonstration mode
    'demo': [
    ],
}
