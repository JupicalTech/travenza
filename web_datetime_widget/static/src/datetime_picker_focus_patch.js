/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { DateTimePicker } from "@web/core/datetime/datetime_picker";
import { MIN_VALID_DATE, today } from "@web/core/l10n/dates";

// Stock behaviour: when a date field has no value yet, its calendar always
// opens on today's month, regardless of any "minDate" set on it - "minDate"
// only clamps the view once it's already computed, it never chooses it.
// That means a dynamic minDate driven by another field (see
// linked_range_datetime_field.js) only affects the opening month when today
// falls before that minDate; if the linked date is in the past relative to
// today, the calendar still opens on the current month.
// This patch makes an explicitly-set minDate (any value other than the
// "no limit" sentinel) the preferred fallback instead of today, so the
// calendar reliably opens on that month either way.
patch(DateTimePicker.prototype, {
    adjustFocus(values, focusedDateIndex) {
        if (!this.shouldAdjustFocusDate && this.state.focusDate) {
            return;
        }
        let dateToFocus = values[focusedDateIndex] || values[focusedDateIndex === 1 ? 0 : 1];
        if (!dateToFocus) {
            dateToFocus = this.minDate.year > MIN_VALID_DATE.year ? this.minDate : today();
        }
        this.state.focusDate = this.clamp(dateToFocus.startOf("month"));
    },
});
