# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import UserError


class ProductLabelLayout(models.TransientModel):
    _inherit = "product.label.layout"

    print_format = fields.Selection(
        selection_add=[
            ("jewelry", "Etiqueta Joyeria"),
        ],
        ondelete={"jewelry": "set default"}
    )

    def _prepare_report_data(self):
        if self.print_format == "jewelry":
            xml_id = "blink_product_label_jewelry.report_product_label_jewelry"

            if self.custom_quantity <= 0:
                raise UserError(_("You need to set a positive quantity."))

            active_model = ""
            if self.product_tmpl_ids:
                products = self.product_tmpl_ids.ids
                active_model = "product.template"
            elif self.product_ids:
                products = self.product_ids.ids
                active_model = "product.product"
            else:
                raise UserError(_("No product to print, if the product is archived please unarchive it before printing its label."))

            data = {
                "active_model": active_model,
                "quantity_by_product": {p: self.custom_quantity for p in products},
                "layout_wizard": self.id,
                "price_included": True,
            }
            return xml_id, data

        return super()._prepare_report_data()
