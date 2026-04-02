from . import models


def _post_init_hook(env):
    """Auto-enable available_in_pos for existing customers (customer_rank > 0)."""
    env['res.partner'].search([
        ('customer_rank', '>', 0),
        ('available_in_pos', '=', False),
    ]).write({'available_in_pos': True})
