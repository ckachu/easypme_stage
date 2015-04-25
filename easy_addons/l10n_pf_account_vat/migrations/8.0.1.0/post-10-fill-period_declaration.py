# -*- coding: utf-8 -*-

import logging
import pooler

__name__="Mise a jour de la periode de declaration s il est vide"
_logger = logging.getLogger('l10n_pf_account_vat')
def migrate(cr,v):
    import pdb
    pdb.set_trace()
    pool = pooler.get_pool(cr.dbname)
    user_obj = pool.get('res.users')
    uid = 1
    context = user_obj.context_get(cr, uid)

    #On recupere les declarations qui ont le champ period_declaration vide
    declaration_obj = pool.get('l10n.pf.account.vat.declaration')
    declaration_ids = declaration_obj.search(cr, uid, [('period_declaration', '=', False)], context=context)

    #On recupere la valeur de period_declaration dans res.company
    company_obj = pool.get('res.company')
    period_dec = company_obj.browse(cr, uid, uid, context=context).period_declaration

    #On met la valeur dans le champ vide de toutes les déclarations
    for i in declaration_obj.browse(cr, uid, declaration_ids, context=context):
        i.write(cr, uid, uid, {'period_declaration': period_dec}, context=context)

