from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    available_in_pos = fields.Boolean(
        string='POS',
        default=False,
        help='If checked, this contact will be available for selection in Point of Sale.',
    )

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields = super()._load_pos_data_fields(config_id)
        fields.append('available_in_pos')
        return fields

    @api.model_create_multi
    def create(self, vals_list):
        partners = super().create(vals_list)
        # Auto-enable for POS if created from within an active POS session
        pos_session = self.env['pos.session'].sudo().search([
            ('user_id', '=', self.env.uid),
            ('state', '=', 'opened'),
        ], limit=1)
        if pos_session:
            partners.filtered(lambda p: not p.available_in_pos).write({
                'available_in_pos': True,
            })
        return partners
