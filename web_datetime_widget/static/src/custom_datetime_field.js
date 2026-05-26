/** @odoo-module **/

import { onWillRender, useEffect, useRef, useState } from "@odoo/owl";
import { useDateTimePicker } from "@web/core/datetime/datetime_picker_hook";
import { areDatesEqual } from "@web/core/l10n/dates";
import { formatDateTime } from "@web/views/fields/formatters";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { exprToBoolean } from "@web/core/utils/strings";
import { DateTimeField, dateTimeField } from "@web/views/fields/datetime/datetime_field";

export class CustomDateTimeField extends DateTimeField {
    static props = {
        ...super.props,
        showTime: { type: Boolean, optional: true },
    };

    static template = "web.DateTimeField";

    setup() {
        const getPickerProps = () => {
            const rawValue = this.getRecordValue();
            const value = Array.isArray(rawValue)
                ? rawValue.map(v => v ?? false)
                : (rawValue ?? false);
            const pickerProps = {
                value,
                type: this.props.showTime ? "datetime" : "date",
                range: this.isRange(value),
                // format: this.props.showTime ? "dd/MM/yyyy HH:mm:ss" : "dd/MM/yyyy",
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
                    [toUpdate[this.startDateField], toUpdate[this.endDateField]] = this.state.value;
                } else {
                    toUpdate[this.props.name] = this.state.value;
                }
                if (!this.startDateField || !this.endDateField) {
                    for (const fieldName in toUpdate) {
                        if (areDatesEqual(toUpdate[fieldName], this.props.record.data[fieldName])) {
                            delete toUpdate[fieldName];
                        }
                    }
                } else {
                    if (
                        areDatesEqual(toUpdate[this.startDateField], this.props.record.data[this.startDateField]) &&
                        areDatesEqual(toUpdate[this.endDateField], this.props.record.data[this.endDateField])
                    ) {
                        delete toUpdate[this.startDateField];
                        delete toUpdate[this.endDateField];
                    }
                }

                if (Object.keys(toUpdate).length) {
                    this.props.record.update(toUpdate);
                }
            },
        });

        this.state = useState(dateTimePicker.state);
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
            const fix = (inputEl, valueIndex) => {
                if (!inputEl || inputEl !== document.activeElement) {
                } else {
                    return;
                }
                if (!this.values) return;
                const lux = this.values[valueIndex];
                if (!lux) return;
                const correct = this.props.showTime && this.field.type !== "date"
                    ? formatDateTime(lux)
                    : lux.toFormat("dd/MM/yyyy");
                if (correct && inputEl && inputEl.value && inputEl.value !== correct) {
                    inputEl.value = correct;
                }
            };
            fix(this.startDate.el, 0);
            fix(this.endDate.el, 1);
        });
    }

    getFormattedValue(valueIndex) {
        const value = this.values?.[valueIndex];
        if (!value) return "";
        if (this.props.showTime && this.field.type !== "date") {
            return formatDateTime(value);
        }
        return value.toFormat("dd/MM/yyyy");
    }

    get formattedValue() {
        const value = this.values?.[0];
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
    supportedOptions: [...dateTimeField.supportedOptions],
    extractProps: ({ attrs, options }, dynamicInfo) => ({
        ...dateTimeField.extractProps({ attrs, options }, dynamicInfo),
        showTime: exprToBoolean(options.showTime ?? false),
    }),
    supportedTypes: ["datetime", "date"],
};

registry.category("fields").add("custom_datetime", customDateTimeField);