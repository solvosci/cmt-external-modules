# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def ts_get_grid_structure(self, template_id, partner_id, pricelist_id):
        res = {
            'column_attrs': [],
            'row_attrs': [],
            'str_table': {}
        }
        template = self.browse(template_id)
        num_attrs = len(template.attribute_line_ids)
        if not template or not (num_attrs > 1):
            return res
        line_x = template.attribute_line_ids[0]
        line_y = False if num_attrs == 1 else template.attribute_line_ids[1]

        ctx = self._context.copy()
        ctx.update(pricelist=pricelist_id, partner=partner_id)
        t_product = self.env['product.product']
        stock_field = t_product._get_stock_field()
        fields = ['id', stock_field, 'price', 'taxes_id']
        read = template.with_context(ctx).product_variant_ids.read(fields)
        variant_dic = {}
        for dic in read:
            variant_dic[dic['id']] = dic

        for value_x in line_x.value_ids:
            x_attr = {
                'id': value_x.id,
                'name': value_x.name
            }
            res['column_attrs'].append(x_attr)
            res['str_table'][value_x.id] = {}
            for value_y in line_y.value_ids:
                y_attr = {
                    'id': value_y.id,
                    'name': value_y.name
                }
                if y_attr not in res['row_attrs']:
                    res['row_attrs'].append(y_attr)
                values = value_x
                if value_y:
                    values += value_y
                product = template.product_variant_ids.filtered(
                    lambda x: not(values - x.attribute_value_ids))[:1]

                var_info = variant_dic[product.id]
                tax_ids = product._ts_compute_taxes(product,
                                                    var_info['taxes_id'],
                                                    partner_id)
                cell_dic = {
                    'id': product and product.id or 0,
                    'stock': var_info[stock_field],
                    'price': var_info['price'],
                    'discount': 0.0,
                    'qty': 0.0,
                    'tax_ids': tax_ids,
                    'enable': True if product else False
                }
                res['str_table'][value_x.id][value_y.id] = cell_dic
        return res
