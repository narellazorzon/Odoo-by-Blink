# -*- coding: utf-8 -*-
from collections import defaultdict
from odoo import _, models
from odoo.exceptions import UserError


class ReportProductLabel2x4(models.AbstractModel):
    _name = 'report.blink_product_label_2x4.label_2x4'
    _description = 'Product Label 2x4 Report'

    def _get_report_values(self, docids, data):
        layout_wizard = self.env['product.label.layout'].browse(data.get('layout_wizard'))

        if data.get('active_model') == 'product.template':
            Product = self.env['product.template'].with_context(display_default_code=False)
        elif data.get('active_model') == 'product.product':
            Product = self.env['product.product'].with_context(display_default_code=False)
        else:
            raise UserError(_('Product model not defined, Please contact your administrator.'))

        if not layout_wizard:
            return {}

        total = 0
        qty_by_product_in = data.get('quantity_by_product')
        products = Product.search([('id', 'in', [int(p) for p in qty_by_product_in.keys()])], order='name desc')
        quantity_by_product = defaultdict(list)
        
        for product in products:
            q = qty_by_product_in[str(product.id)]
            quantity_by_product[product].append((product.barcode, q))
            total += q

        return {
            'quantity': quantity_by_product,
            'page_numbers': total,
            'price_included': data.get('price_included'),
            'pricelist': layout_wizard.pricelist_id,
        }
