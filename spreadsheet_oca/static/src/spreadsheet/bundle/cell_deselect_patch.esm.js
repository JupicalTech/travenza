// import {components} from "@odoo/o-spreadsheet";
// import {patch} from "@web/core/utils/patch";

// const {Grid} = components;

// function splitZoneExcludingCell(zone, col, row) {
//     const result = [];
//     if (row > zone.top) {
//         result.push({left: zone.left, right: zone.right, top: zone.top, bottom: row - 1});
//     }
//     if (row < zone.bottom) {
//         result.push({left: zone.left, right: zone.right, top: row + 1, bottom: zone.bottom});
//     }
//     if (col > zone.left) {
//         result.push({left: zone.left, right: col - 1, top: row, bottom: row});
//     }
//     if (col < zone.right) {
//         result.push({left: col + 1, right: zone.right, top: row, bottom: row});
//     }
//     return result;
// }

// function addZoneToSelection(selection, zone) {
//     const result = selection.processEvent({
//         anchor: {
//             zone: zone,
//             cell: {col: zone.left, row: zone.top},
//         },
//         mode: "newAnchor",
//         options: {scrollIntoView: false},
//     });
// }

// function setZoneAsSelection(selection, zone) {
//     const result = selection.processEvent({
//         anchor: {
//             zone: zone,
//             cell: {col: zone.left, row: zone.top},
//         },
//         mode: "overrideSelection",
//         options: {scrollIntoView: false},
//     });
// }

// patch(Grid.prototype, {
//     onCellClicked(col, row, modifiers, ev) {
//         if (modifiers.addZone) {
//             const model = this.env.model;
//             const zones = model.getters.getSelectedZones();

//             const matchIndex = zones.findIndex(
//                 (z) => col >= z.left && col <= z.right && row >= z.top && row <= z.bottom
//             );

//             if (matchIndex !== -1) {
//                 const matchedZone = zones[matchIndex];
//                 const isSingleCell = matchedZone.left === matchedZone.right &&
//                                      matchedZone.top === matchedZone.bottom;

//                 if (zones.length > 1 || !isSingleCell) {
//                     const otherZones = zones.filter((_, i) => i !== matchIndex);
//                     const splitZones = splitZoneExcludingCell(matchedZone, col, row);
//                     const remaining = [...otherZones, ...splitZones];


//                     if (remaining.length === 0) {
//                         return;
//                     }

//                     setZoneAsSelection(model.selection, remaining[0]);
//                     for (let i = 1; i < remaining.length; i++) {
//                         addZoneToSelection(model.selection, remaining[i]);
//                     }

//                     ev.preventDefault();
//                     return;
//                 }
//             }
//         }
//         super.onCellClicked(col, row, modifiers, ev);
//     },
// });


// document.addEventListener("paste", (ev) => {
//     if (!ev.clipboardData) return;
//     const html = ev.clipboardData.getData("text/html");
//     if (!html.includes("data-osheet-clipboard")) return;
//     const plain = ev.clipboardData.getData("text/plain");
//     if (!plain.trim()) return;


//     const lines = plain.trim().split("\n");
//     const dataLines = lines.slice(1);
//     const allNumeric = dataLines.length > 0 && dataLines.every(line =>
//         line.split("\t").every(cell => {
//             const t = cell.trim();
//             return t === "" || !isNaN(Number(t.replace(/,/g, "")));
//         })
//     );

//     if (allNumeric) {
//         const original = ev.clipboardData.getData.bind(ev.clipboardData);
//         ev.clipboardData.getData = function(type) {
//             if (type === "text/html") return "";
//             return original(type);
//         };
//     }
// }, true);





import * as spreadsheet from "@odoo/o-spreadsheet";
import {patch} from "@web/core/utils/patch";

const {components} = spreadsheet;
const {Grid} = components;
const {cellMenuRegistry} = spreadsheet.registries;

function splitZoneExcludingCell(zone, col, row) {
    const result = [];
    if (row > zone.top) {
        result.push({left: zone.left, right: zone.right, top: zone.top, bottom: row - 1});
    }
    if (row < zone.bottom) {
        result.push({left: zone.left, right: zone.right, top: row + 1, bottom: zone.bottom});
    }
    if (col > zone.left) {
        result.push({left: zone.left, right: col - 1, top: row, bottom: row});
    }
    if (col < zone.right) {
        result.push({left: col + 1, right: zone.right, top: row, bottom: row});
    }
    return result;
}

function addZoneToSelection(selection, zone) {
    selection.processEvent({
        anchor: {
            zone: zone,
            cell: {col: zone.left, row: zone.top},
        },
        mode: "newAnchor",
        options: {scrollIntoView: false},
    });
}

function setZoneAsSelection(selection, zone) {
    selection.processEvent({
        anchor: {
            zone: zone,
            cell: {col: zone.left, row: zone.top},
        },
        mode: "overrideSelection",
        options: {scrollIntoView: false},
    });
}

patch(Grid.prototype, {
    onCellClicked(col, row, modifiers, ev) {
        if (modifiers.addZone) {
            const model = this.env.model;
            const zones = model.getters.getSelectedZones();

            const matchIndex = zones.findIndex(
                (z) => col >= z.left && col <= z.right && row >= z.top && row <= z.bottom
            );

            if (matchIndex !== -1) {
                const matchedZone = zones[matchIndex];
                const isSingleCell = matchedZone.left === matchedZone.right &&
                                     matchedZone.top === matchedZone.bottom;

                if (zones.length > 1 || !isSingleCell) {
                    const otherZones = zones.filter((_, i) => i !== matchIndex);
                    const splitZones = splitZoneExcludingCell(matchedZone, col, row);
                    const remaining = [...otherZones, ...splitZones];

                    if (remaining.length === 0) {
                        return;
                    }

                    setZoneAsSelection(model.selection, remaining[0]);
                    for (let i = 1; i < remaining.length; i++) {
                        addZoneToSelection(model.selection, remaining[i]);
                    }

                    ev.preventDefault();
                    return;
                }
            }
        }
        super.onCellClicked(col, row, modifiers, ev);
    },
});


cellMenuRegistry.content["convert_to_number"] = {
    name: "Convert to Number",
    sequence: 200,
    isVisible: (env) => true,
    execute: (env) => {
        const zones = env.model.getters.getSelectedZones();
        const sheetId = env.model.getters.getActiveSheetId();
        for (const zone of zones) {
            for (let row = zone.top; row <= zone.bottom; row++) {
                for (let col = zone.left; col <= zone.right; col++) {
                    const cell = env.model.getters.getCell({sheetId, col, row});
                    const cellContent = env.model.getters.getCellText ? env.model.getters.getCellText({sheetId, col, row}) : null;
                   
                    if (cell || cellContent) {
                        const v = (cellContent || cell?.content || "").trim().replace(/,/g, "");
                       
                        if (v !== "" && !isNaN(Number(v))) {
                            env.model.dispatch("UPDATE_CELL", {
                                sheetId,
                                col,
                                row,
                                content: String(Number(v)),
                                format: "",
                            });
                        }
                    }
                }
            }
        }
    },
};


document.addEventListener("paste", (ev) => {
    if (!ev.clipboardData) return;
    const html = ev.clipboardData.getData("text/html");
    if (!html.includes("data-osheet-clipboard")) return;
    const plain = ev.clipboardData.getData("text/plain");
    if (!plain.trim()) return;

    const lines = plain.trim().split("\n");
    const dataLines = lines.slice(1);
    const allNumeric = dataLines.length > 0 && dataLines.every(line =>
        line.split("\t").every(cell => {
            const t = cell.trim();
            return t === "" || !isNaN(Number(t.replace(/,/g, "")));
        })
    );

    if (allNumeric) {
        const original = ev.clipboardData.getData.bind(ev.clipboardData);
        ev.clipboardData.getData = function(type) {
            if (type === "text/html") return "";
            return original(type);
        };
    }
}, true);



