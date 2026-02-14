/** @odoo-module **/

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    async afterOrderValidation() {
        // Fetch AFIP data ANTES de mostrar el receipt screen
        const order = this.currentOrder;
        if (order && order.is_electronic_invoice && order.raw.account_move) {
            try {
                const afipData = await this.pos.data.call(
                    "pos.order",
                    "get_afip_receipt_data",
                    [[order.id]]
                );
                order._afip_receipt_data = afipData || null;
            } catch (e) {
                console.warn("Could not fetch AFIP receipt data:", e);
                order._afip_receipt_data = null;
            }
        }
        await super.afterOrderValidation(...arguments);
    },
});
