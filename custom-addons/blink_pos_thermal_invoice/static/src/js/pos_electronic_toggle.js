/** @odoo-module **/

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this._initElectronicInvoice();
    },

    onMounted() {
        super.onMounted(...arguments);
        this._initElectronicInvoice();
    },

    _initElectronicInvoice() {
        if (!this.pos.config.thermal_electronic_invoice) {
            return;
        }
        const order = this.currentOrder;
        if (order && order._electronic_invoice_initialized === undefined) {
            order._electronic_invoice_initialized = true;
            order.is_electronic_invoice = true;
            order.set_to_invoice(true);
        }
    },

    get isElectronicInvoiceEnabled() {
        return this.pos.config.thermal_electronic_invoice || false;
    },

    get isElectronicInvoice() {
        return this.currentOrder?.is_electronic_invoice || false;
    },

    toggleElectronicInvoice() {
        const order = this.currentOrder;
        if (!order) {
            return;
        }
        const newValue = !order.is_electronic_invoice;
        order.is_electronic_invoice = newValue;
        order.set_to_invoice(newValue);
    },

    toggleIsToInvoice() {
        // Si la factura electrónica térmica está habilitada,
        // no permitir cambiar to_invoice directamente
        if (this.pos.config.thermal_electronic_invoice) {
            return;
        }
        super.toggleIsToInvoice(...arguments);
    },
});
