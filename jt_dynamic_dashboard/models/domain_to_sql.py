# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2024-TODAY Jupical Technologies(<http://www.jupical.io>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.io>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models


def get_query(self, args, operation, field, group_by=False, apply_ir_rules=False):

    query = self._search(args)
    join = ''
    group_by_str = ''
    
    if apply_ir_rules:
        self._apply_ir_rules(query, 'read')
        
    if operation and field:
        data = 'COALESCE(%s("%s".%s),0) AS value' % (operation.upper(), self._table, field.name)
        if group_by:
            if group_by.ttype == 'many2one':
                relation_model = group_by.relation.replace('.', '_')
                join = ' INNER JOIN %s on "%s".id = "%s".%s' % (
                    relation_model, relation_model, self._table, group_by.name)
                rec_name = self.env[group_by.relation]._rec_name_fallback()
                data = data + ',"%s".%s AS %s' % (
                    relation_model, rec_name, group_by.name)
                group_by_str = ' Group by "%s".%s' % (relation_model, rec_name)
            else:
                data = data + ',"%s".%s' % (self._table, group_by.name)
                group_by_str = ' Group by "%s".%s' % (
                    self._table, str(group_by.name))
    else:
        data = '"%s".id' % (self._table)

    from_clause, from_params = query.from_clause
    where_clause, where_clause_params = query.where_clause
    where_str = where_clause and (" WHERE %s" % where_clause) or ''
    

    query_str = 'SELECT %s FROM ' % data + from_clause + join + where_str + group_by_str
    def format_param(x):
        if not isinstance(x, tuple):
            return "'" + str(x) + "'"
        elif isinstance(x, tuple) and len(x) == 1:
            return "(" + str(x[0]) + ")"
        else:
            return str(x)
    exact_query = query_str % tuple(map(format_param, where_clause_params))
    return exact_query

models.BaseModel.get_query = get_query



