/** @odoo-module **/

// TODO v19: added useRef, useEffect for picker.activeInput support
import { Component, onWillRender, useEffect, useRef, useState } from "@odoo/owl";
import { useDateTimePicker } from "@web/core/datetime/datetime_picker_hook";
import { areDatesEqual } from "@web/core/l10n/dates";
import { formatDate, formatDateTime } from "@web/views/fields/formatters";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { exprToBoolean } from "@web/core/utils/strings";
import { DateTimeField, dateTimeField } from "@web/views/fields/datetime/datetime_field";

/**
 * @typedef {luxon.DateTime} DateTime
 *
 
 * @typedef {import("../standard_field_props").StandardFieldProps & {
 *  endDateField?: string;
 *  maxDate?: string;
 *  minDate?: string;
 *  placeholder?: string;
 *  required?: boolean;
 *  rounding?: number;
 *  startDateField?: string;
 *  warnFuture?: boolean;
 *  showTime?: boolean;
 * }} DateTimeFieldProps
 *
 * @typedef {import("@web/core/datetime/datetime_picker").DateTimePickerProps} DateTimePickerProps
 */

/** @extends {Component<DateTimeFieldProps>} */
export class CustomDateTimeField extends DateTimeField {
    static props = {
        ...super.props,
        showTime: { type: Boolean, optional: true },
    };

    static template = "web.DateTimeField";

    //-------------------------------------------------------------------------
    // Lifecycle
    //-------------------------------------------------------------------------

    setup() {
        const getPickerProps = () => {
            const value = this.getRecordValue();
            /** @type {DateTimePickerProps} */
            const pickerProps = {
                value,
                type: this.props.showTime ? 'datetime' : 'date',
                range: this.isRange(value),
            };
            if (this.props.maxDate) {
                pickerProps.maxDate = this.parseLimitDate(this.props.maxDate);
            }
            if (this.props.minDate) {
                pickerProps.minDate = this.parseLimitDate(this.props.minDate);
            }
            if (!isNaN(this.props.rounding)) {
                pickerProps.rounding = this.props.rounding;
            }
            return pickerProps;
        };

        const dateTimePicker = useDateTimePicker({
            target: "root",
            get pickerProps() {
                return getPickerProps();
            },
            onChange: () => {
                this.state.range = this.isRange(this.state.value);
            },
            onApply: () => {
                const toUpdate = {};
                if (Array.isArray(this.state.value)) {
                    // Value is already a range
                    [toUpdate[this.startDateField], toUpdate[this.endDateField]] = this.state.value;
                } else {
                    toUpdate[this.props.name] = this.state.value;
                }
                // when startDateField and endDateField are set, and one of them has changed, we keep
                // the unchanged one to make sure ORM protects both fields from being recomputed by the
                // server, ORM team will handle this properly on master, then we can remove unchanged values
                if (!this.startDateField || !this.endDateField) {
                    // If startDateField or endDateField are not set, delete unchanged fields
                    for (const fieldName in toUpdate) {
                        if (areDatesEqual(toUpdate[fieldName], this.props.record.data[fieldName])) {
                            delete toUpdate[fieldName];
                        }
                    }
                } else {
                    // If both startDateField and endDateField are set, check if they haven't changed
                    if (areDatesEqual(toUpdate[this.startDateField], this.props.record.data[this.startDateField]) &&
                        areDatesEqual(toUpdate[this.endDateField], this.props.record.data[this.endDateField])) {
                        delete toUpdate[this.startDateField];
                        delete toUpdate[this.endDateField];
                    }
                }

                if (Object.keys(toUpdate).length) {
                    this.props.record.update(toUpdate);
                }
            },
        });
        // Subscribes to changes made on the picker state
        this.state = useState(dateTimePicker.state);
        // TODO v19: picker.activeInput required by v19 DateTimeField template
        this.picker = useState({ activeInput: "" });
        this.openPicker = dateTimePicker.open;

        this.startDate = useRef("start-date");
        this.endDate = useRef("end-date");

        useEffect(
            () => {
                [this.startDate, this.endDate].forEach((ref, index) => {
                    if (ref.el?.getAttribute("data-field") === this.picker.activeInput) {
                        ref.el.focus();
                        this.openPicker(index);
                    }
                });
            },
            () => [this.startDate.el?.tagName, this.endDate.el?.tagName, this.picker.activeInput]
        );

        onWillRender(() => this.triggerIsDirty());


        useEffect(() => {
    const inputs = document.querySelectorAll('.o_field_custom_datetime input, .o_field_datetime input');
    inputs.forEach(input => {
        if (!input.value) return;
        const parts = input.value.split('/');
        if (parts.length === 3 && parts[0].length <= 2 && parts[1].length <= 2) {
            const [mm, dd, yyyy] = parts;
            if (!isNaN(mm) && !isNaN(dd) && !isNaN(yyyy)) {
                input.value = `${dd.padStart(2,'0')}/${mm.padStart(2,'0')}/${yyyy}`;
            }
        }
    });
});


    }

    //-------------------------------------------------------------------------
    // Methods
    //-------------------------------------------------------------------------

    /**
     * @param {number} valueIndex
     */
    // getFormattedValue(valueIndex) {
    //     const value = this.values[valueIndex];
    //     return value
    //         ? this.props.showTime && this.field.type !== "date"
    //             ? formatDateTime(value)
    //             : formatDate(value)
    //         : "";
    // }

//     getFormattedValue(valueIndex) {
//     const value = this.values[valueIndex];
//     return value
//         ? this.props.showTime && this.field.type !== "date"
//             ? formatDateTime(value)
//             : formatDate(value, { numeric: true })
//         : "";
// }

        getFormattedValue(valueIndex) {
            const value = this.values[valueIndex];
            if (!value) return "";
            if (this.props.showTime && this.field.type !== "date") {
                return formatDateTime(value);
            }
            return value.toFormat("dd/MM/yyyy");
        }

        get formattedValue() {
            const value = this.values[0];
            if (!value) return "";
            if (this.props.showTime && this.field.type !== "date") {
                return formatDateTime(value);
            }
            return value.toFormat("dd/MM/yyyy");
    }
}

export const customDateTimeField = {
    ...dateTimeField,
    component: CustomDateTimeField,
    displayName: _t("Custom Date & Time"),
    supportedOptions: [
        ...dateTimeField.supportedOptions,
    ],
    extractProps: ({ attrs, options }, dynamicInfo) => ({
        ...dateTimeField.extractProps({ attrs, options }, dynamicInfo),
        showTime: exprToBoolean(options.showTime ?? false),
    }),
    supportedTypes: ["datetime"],
};

registry
    .category("fields")
    .add("custom_datetime", customDateTimeField);
