/**
 * Manage object actions modal (V0.4.0e).
 */

import {
  buildAddObjectAction,
  buildRemoveObjectAction,
  postCommand,
} from "./api.js";
import { normalizeSnapshot } from "./snapshot.js";
import { attachTemplateVarHelp } from "./templateVarsHelp.js";

const EFFECT_CHOICES = [
  { id: "none", label: "None" },
  { id: "delete_self", label: "delete_self — remove object" },
  { id: "random_move_self", label: "random_move_self — move object randomly" },
  { id: "move_area", label: "move_area — transfer agent to another area" },
];

let getSnapshot = () => null;
let onStateChanged = async () => {};
let showToast = () => {};
let modalTitle;
let modalForm;
let modalError;
let modalBackdrop;
let closeModal;

/** @type {{ id: string, name: string, actions?: string[], actions_detail?: Record<string, object> } | null} */
let manageObject = null;

export function initObjectActions(deps) {
  getSnapshot = deps.getSnapshotFn;
  onStateChanged = deps.onStateChangedFn;
  showToast = deps.showToastFn;
  modalTitle = deps.modalTitleEl;
  modalForm = deps.modalFormEl;
  modalError = deps.modalErrorEl;
  modalBackdrop = deps.modalBackdropEl;
  closeModal = deps.closeModal;
}

function listAreaIds() {
  const snap = normalizeSnapshot(getSnapshot());
  if (!snap?.areas) return [];
  return Object.keys(snap.areas).sort();
}

function formatEffectSummary(action) {
  const effects = action?.effects || [];
  if (effects.length === 0) return "no effect";
  return effects
    .map((effect) => {
      if (effect.name === "move_area") {
        const area = effect.params?.["dest-area"] || "?";
        const at = effect.params?.["dest-at"] || "?";
        return `move_area → ${area} (${at})`;
      }
      return effect.name;
    })
    .join(", ");
}

function formatActionSummary(action) {
  const kind = action?.kind || "interact";
  const kindLabel = kind === "trigger" ? "trigger" : "interact";
  let suffix = formatEffectSummary(action);
  if (kind === "trigger") {
    const flags = [];
    if (action?.halt_movement) flags.push("halt");
    if (action?.delete_after_trigger === false) flags.push("reusable");
    if (flags.length) suffix += ` · ${flags.join(", ")}`;
  }
  return `${kindLabel} · ${suffix}`;
}

function actionNames() {
  const detail = manageObject?.actions_detail || {};
  if (manageObject?.actions?.length) {
    return [...manageObject.actions].sort();
  }
  return Object.keys(detail).sort();
}

async function refreshManagedObject() {
  const snap = normalizeSnapshot(getSnapshot());
  for (const block of Object.values(snap?.areas || {})) {
    const found = (block.objects || []).find((o) => o.id === manageObject?.id);
    if (found) {
      manageObject = found;
      return;
    }
  }
}

async function runCommand(line) {
  const result = await postCommand(line);
  if (!result.ok) throw new Error(result.message);
  showToast(result.message, false);
  if (result.snapshot) {
    await onStateChanged(result.snapshot);
  } else {
    await onStateChanged();
  }
}

function showManageModal() {
  if (!manageObject) return;

  modalTitle.textContent = `Manage actions — ${manageObject.name}`;
  modalForm.innerHTML = "";
  modalError.textContent = "";

  const names = actionNames();
  if (names.length === 0) {
    const empty = document.createElement("p");
    empty.className = "panel-empty";
    empty.textContent = "No actions yet.";
    modalForm.appendChild(empty);
  } else {
    const list = document.createElement("ul");
    list.className = "action-list";
    const detail = manageObject.actions_detail || {};

    for (const name of names) {
      const action = detail[name] || {};
      const li = document.createElement("li");
      li.className = "action-list-item";

      const label = document.createElement("span");
      label.className = "action-list-label";
      label.textContent = `${name} (range ${action.range ?? "?"}) · ${formatActionSummary(action)}`;

      const buttons = document.createElement("div");
      buttons.className = "action-list-buttons";

      const editBtn = document.createElement("button");
      editBtn.type = "button";
      editBtn.textContent = "Edit";
      editBtn.addEventListener("click", () => openActionForm(name, action));

      const removeBtn = document.createElement("button");
      removeBtn.type = "button";
      removeBtn.textContent = "Remove";
      removeBtn.addEventListener("click", () => removeAction(name));

      buttons.appendChild(editBtn);
      buttons.appendChild(removeBtn);
      li.appendChild(label);
      li.appendChild(buttons);
      list.appendChild(li);
    }
    modalForm.appendChild(list);
  }

  const actions = document.createElement("div");
  actions.className = "modal-actions";

  const addBtn = document.createElement("button");
  addBtn.type = "button";
  addBtn.textContent = "Add action…";
  addBtn.addEventListener("click", () => openActionForm(null, null));
  actions.appendChild(addBtn);

  modalForm.appendChild(actions);
  modalBackdrop.classList.remove("hidden");
}

export function openManageObjectActionsModal(entity) {
  manageObject = entity;
  showManageModal();
}

async function removeAction(name) {
  if (!window.confirm(`Remove action "${name}" from ${manageObject.name}?`)) return;
  try {
    await runCommand(buildRemoveObjectAction(manageObject.id, name));
    await refreshManagedObject();
    showManageModal();
  } catch (err) {
    modalError.textContent = String(err.message || err);
  }
}

function parseEffectFromAction(action) {
  const effects = action?.effects || [];
  if (effects.length === 0) {
    return { effect: "none", destArea: "", destX: "0", destY: "0" };
  }
  const first = effects[0];
  if (first.name === "move_area") {
    const parts = String(first.params?.["dest-at"] || "0,0").split(",");
    return {
      effect: "move_area",
      destArea: first.params?.["dest-area"] || "",
      destX: (parts[0] || "0").trim(),
      destY: (parts[1] || "0").trim(),
    };
  }
  return { effect: first.name, destArea: "", destX: "0", destY: "0" };
}

function openActionForm(existingName, existingAction) {
  const isEdit = existingName != null;
  const parsed = isEdit
    ? parseEffectFromAction(existingAction)
    : { effect: "none", destArea: "", destX: "0", destY: "0" };
  const areas = listAreaIds();
  const defaultDestArea = parsed.destArea || areas[0] || "room";

  const actionKind = existingAction?.kind || "interact";

  modalTitle.textContent = isEdit
    ? `Edit action — ${existingName}`
    : `Add action — ${manageObject.name}`;
  modalForm.innerHTML = "";
  modalError.textContent = "";

  const kindWrap = document.createElement("label");
  kindWrap.className = "modal-field";
  const kindLabel = document.createElement("span");
  kindLabel.textContent = "Kind";
  kindWrap.appendChild(kindLabel);
  const kindSelect = document.createElement("select");
  kindSelect.name = "kind";
  for (const choice of [
    { id: "interact", label: "interact — LLM compound-turn action" },
    { id: "trigger", label: "trigger — fires on path step (area event)" },
  ]) {
    const opt = document.createElement("option");
    opt.value = choice.id;
    opt.textContent = choice.label;
    if (choice.id === actionKind) opt.selected = true;
    kindSelect.appendChild(opt);
  }
  kindWrap.appendChild(kindSelect);
  modalForm.appendChild(kindWrap);

  const fields = [
    {
      name: "name",
      label: "Action name",
      value: existingName ?? "enter",
      required: true,
    },
    {
      name: "range",
      label: "Range (Chebyshev tiles)",
      value: String(existingAction?.range ?? (actionKind === "trigger" ? 0 : 1)),
      type: "number",
      required: true,
    },
    {
      name: "result",
      label: "Result (agent sees)",
      value: existingAction?.result ?? (actionKind === "trigger" ? "(trigger)" : "You interact with it."),
      type: "textarea",
      required: true,
      templateHelp: true,
      interactOnly: true,
    },
    {
      name: "passive",
      label: "Passive / area event text",
      value:
        existingAction?.passive_result ??
        (actionKind === "trigger"
          ? "{actor} triggers it."
          : "{actor} interacts with it."),
      type: "textarea",
      required: true,
      templateHelp: true,
    },
  ];

  for (const field of fields) {
    const wrap = document.createElement("label");
    wrap.className = "modal-field";
    if (field.interactOnly) {
      wrap.classList.add("modal-field-conditional");
      wrap.dataset.showWhenField = "kind";
      wrap.dataset.showWhenValues = "interact";
    }
    const label = document.createElement("span");
    label.className = "modal-field-label-row";
    label.textContent = field.label;
    if (field.templateHelp) attachTemplateVarHelp(label);
    wrap.appendChild(label);

    let input;
    if (field.type === "textarea") {
      input = document.createElement("textarea");
      input.rows = 2;
      input.value = field.value ?? "";
    } else {
      input = document.createElement("input");
      input.type = field.type || "text";
      input.value = field.value ?? "";
    }
    input.name = field.name;
    if (field.required) input.required = true;
    wrap.appendChild(input);
    modalForm.appendChild(wrap);
  }

  const triggerFields = document.createElement("div");
  triggerFields.className = "action-trigger-fields";

  const haltWrap = document.createElement("label");
  haltWrap.className = "modal-field";
  const haltLabel = document.createElement("span");
  haltLabel.textContent = "Halt movement on trigger";
  haltWrap.appendChild(haltLabel);
  const haltInput = document.createElement("input");
  haltInput.type = "checkbox";
  haltInput.name = "haltMovement";
  haltInput.checked = existingAction?.halt_movement ?? true;
  haltWrap.appendChild(haltInput);
  triggerFields.appendChild(haltWrap);

  const deleteWrap = document.createElement("label");
  deleteWrap.className = "modal-field";
  const deleteLabel = document.createElement("span");
  deleteLabel.textContent = "Delete object after trigger";
  deleteWrap.appendChild(deleteLabel);
  const deleteInput = document.createElement("input");
  deleteInput.type = "checkbox";
  deleteInput.name = "deleteAfterTrigger";
  deleteInput.checked = existingAction?.delete_after_trigger !== false;
  deleteWrap.appendChild(deleteInput);
  triggerFields.appendChild(deleteWrap);

  const exceptionsWrap = document.createElement("label");
  exceptionsWrap.className = "modal-field";
  const exceptionsLabel = document.createElement("span");
  exceptionsLabel.textContent = "Trigger exceptions (agent ids)";
  exceptionsWrap.appendChild(exceptionsLabel);
  const exceptionsInput = document.createElement("input");
  exceptionsInput.type = "text";
  exceptionsInput.name = "triggerExceptions";
  exceptionsInput.value = (existingAction?.trigger_exceptions || []).join(", ");
  exceptionsWrap.appendChild(exceptionsInput);
  triggerFields.appendChild(exceptionsWrap);

  modalForm.appendChild(triggerFields);

  const effectWrap = document.createElement("label");
  effectWrap.className = "modal-field modal-field-conditional";
  effectWrap.dataset.showWhenField = "kind";
  effectWrap.dataset.showWhenValues = "interact";
  const effectLabel = document.createElement("span");
  effectLabel.textContent = "Effect";
  effectWrap.appendChild(effectLabel);
  const effectSelect = document.createElement("select");
  effectSelect.name = "effect";
  for (const choice of EFFECT_CHOICES) {
    const opt = document.createElement("option");
    opt.value = choice.id;
    opt.textContent = choice.label;
    if (choice.id === parsed.effect) opt.selected = true;
    effectSelect.appendChild(opt);
  }
  effectWrap.appendChild(effectSelect);
  modalForm.appendChild(effectWrap);

  const moveFields = document.createElement("div");
  moveFields.className = "action-move-fields modal-field-conditional";
  moveFields.dataset.showWhenField = "kind";
  moveFields.dataset.showWhenValues = "interact";

  const destAreaWrap = document.createElement("label");
  destAreaWrap.className = "modal-field";
  const destAreaLabel = document.createElement("span");
  destAreaLabel.textContent = "Destination area";
  destAreaWrap.appendChild(destAreaLabel);
  const destAreaSelect = document.createElement("select");
  destAreaSelect.name = "destArea";
  for (const areaId of areas) {
    const opt = document.createElement("option");
    opt.value = areaId;
    opt.textContent = areaId;
    if (areaId === defaultDestArea) opt.selected = true;
    destAreaSelect.appendChild(opt);
  }
  destAreaWrap.appendChild(destAreaSelect);
  moveFields.appendChild(destAreaWrap);

  const destRow = document.createElement("div");
  destRow.className = "action-dest-row";

  const destXWrap = document.createElement("label");
  destXWrap.className = "modal-field action-dest-coord";
  const destXLabel = document.createElement("span");
  destXLabel.textContent = "Dest X";
  destXWrap.appendChild(destXLabel);
  const destXInput = document.createElement("input");
  destXInput.type = "number";
  destXInput.name = "destX";
  destXInput.value = parsed.destX;
  destXWrap.appendChild(destXInput);
  destRow.appendChild(destXWrap);

  const destYWrap = document.createElement("label");
  destYWrap.className = "modal-field action-dest-coord";
  const destYLabel = document.createElement("span");
  destYLabel.textContent = "Dest Y";
  destYWrap.appendChild(destYLabel);
  const destYInput = document.createElement("input");
  destYInput.type = "number";
  destYInput.name = "destY";
  destYInput.value = parsed.destY;
  destYWrap.appendChild(destYInput);
  destRow.appendChild(destYWrap);

  moveFields.appendChild(destRow);
  modalForm.appendChild(moveFields);

  const toggleMoveFields = () => {
    moveFields.classList.toggle("hidden", effectSelect.value !== "move_area");
  };
  const syncKindFields = () => {
    const isTrigger = kindSelect.value === "trigger";
    triggerFields.classList.toggle("hidden", !isTrigger);
    for (const wrap of modalForm.querySelectorAll(".modal-field-conditional")) {
      const allowed = (wrap.dataset.showWhenValues || "")
        .split(",")
        .map((v) => v.trim());
      const current = wrap.dataset.showWhenField === "kind" ? kindSelect.value : effectSelect.value;
      wrap.hidden = !allowed.includes(String(current));
    }
    toggleMoveFields();
  };
  effectSelect.addEventListener("change", syncKindFields);
  kindSelect.addEventListener("change", syncKindFields);
  syncKindFields();

  const actions = document.createElement("div");
  actions.className = "modal-actions";

  const backBtn = document.createElement("button");
  backBtn.type = "button";
  backBtn.textContent = "Back";
  backBtn.addEventListener("click", () => showManageModal());

  const submit = document.createElement("button");
  submit.type = "submit";
  submit.textContent = isEdit ? "Save" : "Add";

  actions.appendChild(backBtn);
  actions.appendChild(submit);
  modalForm.appendChild(actions);

  modalForm.onsubmit = async (e) => {
    e.preventDefault();
    modalError.textContent = "";
    const data = {
      name: modalForm.elements.name.value.trim(),
      range: modalForm.elements.range.value.trim(),
      kind: modalForm.elements.kind.value,
      result: modalForm.elements.result?.value?.trim() || "(trigger)",
      passive: modalForm.elements.passive.value.trim(),
      effect: modalForm.elements.effect?.value || "none",
      destArea: modalForm.elements.destArea?.value,
      destX: modalForm.elements.destX?.value?.trim(),
      destY: modalForm.elements.destY?.value?.trim(),
      haltMovement: modalForm.elements.haltMovement?.checked ?? true,
      deleteAfterTrigger: modalForm.elements.deleteAfterTrigger?.checked ?? true,
      triggerExceptions: modalForm.elements.triggerExceptions?.value?.trim() ?? "",
    };
    if (!data.name) {
      modalError.textContent = "Action name is required.";
      return;
    }
    try {
      if (isEdit) {
        await runCommand(buildRemoveObjectAction(manageObject.id, existingName));
      }
      await runCommand(
        buildAddObjectAction(manageObject.id, {
          name: data.name,
          range: data.range,
          result: data.result,
          passive: data.passive,
          kind: data.kind,
          haltMovement: data.kind === "trigger" ? data.haltMovement : undefined,
          deleteAfterTrigger: data.kind === "trigger" ? data.deleteAfterTrigger : undefined,
          triggerExceptions: data.kind === "trigger" ? data.triggerExceptions : undefined,
          effect: data.effect,
          destArea: data.destArea,
          destX: data.destX,
          destY: data.destY,
        }),
      );
      await refreshManagedObject();
      showManageModal();
    } catch (err) {
      modalError.textContent = String(err.message || err);
    }
  };
}
