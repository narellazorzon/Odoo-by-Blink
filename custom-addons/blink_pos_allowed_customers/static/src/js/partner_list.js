/** @odoo-module */
import { PartnerList } from "@point_of_sale/app/screens/partner_list/partner_list";
import { patch } from "@web/core/utils/patch";

patch(PartnerList.prototype, {
    async getNewPartners() {
        const limit = 30;
        let domain = [["available_in_pos", "=", true]];

        if (this.state.query) {
            const search_fields = [
                "name",
                "parent_name",
                ...this.getPhoneSearchTerms(),
                "email",
                "barcode",
                "street",
                "zip",
                "city",
                "state_id",
                "country_id",
                "vat",
            ];
            domain = [
                "&",
                ["available_in_pos", "=", true],
                ...Array(search_fields.length - 1).fill("|"),
                ...search_fields.map((field) => [field, "ilike", this.state.query + "%"]),
            ];
        }

        const result = await this.pos.data.searchRead("res.partner", domain, [], {
            limit: limit,
            offset: this.state.currentOffset,
        });

        return result;
    },
});
