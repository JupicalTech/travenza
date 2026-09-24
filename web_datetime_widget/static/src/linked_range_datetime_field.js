/** @odoo-module **/

import { registry } from "@web/core/registry";
import { CustomDateTimeField, customDateTimeField } from "./custom_datetime_field";

const MIN_DATE_FIELD_OPTION = "min_date_field";

// Extends the custom date widget so its calendar's minimum selectable date
// (and therefore the month it opens on) tracks the live value of another
// field on the same record, instead of a static option. Used to make a
// "date to" field's calendar follow a "date from" field without linking the
// two fields into a single range widget (which would also change how the
// "date from" field itself renders).
export class LinkedRangeDateTimeField extends CustomDateTimeField {
    static props = {
        ...CustomDateTimeField.props,
        minDateField: { type: String, optional: true },
    };

    parseLimitDate(value) {
        if (this.props.minDateField && value === this.props.minDateField) {
            return this.props.record.data[this.props.minDateField] || false;
        }
        return super.parseLimitDate(value);
    }
}

export const linkedRangeDateTimeField = {
    ...customDateTimeField,
    component: LinkedRangeDateTimeField,
    supportedOptions: [...customDateTimeField.supportedOptions],
    extractProps: (fieldInfo, dynamicInfo) => {
        const minDateField = fieldInfo.options[MIN_DATE_FIELD_OPTION];
        return {
            ...customDateTimeField.extractProps(fieldInfo, dynamicInfo),
            minDateField,
            minDate: minDateField || fieldInfo.options.min_date,
        };
    },
    fieldDependencies: (fieldInfo) => {
        const deps = customDateTimeField.fieldDependencies
            ? customDateTimeField.fieldDependencies(fieldInfo)
            : [];
        const minDateField = fieldInfo.options[MIN_DATE_FIELD_OPTION];
        if (minDateField) {
            deps.push({ name: minDateField, type: fieldInfo.type, readonly: false });
        }
        return deps;
    },
};

registry.category("fields").add("linked_custom_datetime", linkedRangeDateTimeField);
