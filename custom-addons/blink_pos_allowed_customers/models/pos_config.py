from odoo import models
from odoo.tools import SQL


class PosConfig(models.Model):
    _inherit = 'pos.config'

    def get_limited_partners_loading(self):
        return self.env.execute_query(SQL("""
            WITH pm AS (
                SELECT partner_id, Count(partner_id) order_count
                FROM pos_order
                GROUP BY partner_id
            )
            SELECT id
            FROM res_partner AS partner
            LEFT JOIN pm ON (partner.id = pm.partner_id)
            WHERE (
                partner.company_id = %s OR partner.company_id IS NULL
            )
            AND partner.available_in_pos = true
            ORDER BY COALESCE(pm.order_count, 0) DESC,
                     NAME
            LIMIT %s;
        """, self.company_id.id, self._get_limited_partner_count()))
