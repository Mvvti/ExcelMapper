let orderInput;
let cennikInput;
let placowkiInput;
let templateInput;
let outputInput;
let dateInput;
let statusLabel;
let logsArea;
let generateButton;
let previewButton;
let progressBar;
let buttonStateTimer;
let fieldToInput = {};
let previewSection;
let previewSummary;
let previewHead;
let previewBody;

function clearButtonStateClasses() {
    generateButton.classList.remove("btn--loading", "btn--success", "btn--error");
}

function setButtonState(state) {
    if (buttonStateTimer) {
        clearTimeout(buttonStateTimer);
        buttonStateTimer = null;
    }

    clearButtonStateClasses();

    if (state === "loading") {
        generateButton.disabled = true;
        generateButton.classList.add("btn--loading");
        generateButton.textContent = "Przetwarzanie...";
        progressBar.classList.add("progress-bar--active");
        return;
    }

    if (state === "success") {
        generateButton.disabled = false;
        generateButton.classList.add("btn--success");
        generateButton.textContent = "Zako\u0144czono \u2705";
        progressBar.classList.remove("progress-bar--active");
        buttonStateTimer = setTimeout(() => setButtonState("default"), 2000);
        return;
    }

    if (state === "error") {
        generateButton.disabled = false;
        generateButton.classList.add("btn--error");
        generateButton.textContent = "B\u0142\u0105d \u274c";
        progressBar.classList.remove("progress-bar--active");
        buttonStateTimer = setTimeout(() => setButtonState("default"), 2000);
        return;
    }

    generateButton.disabled = false;
    generateButton.textContent = "Generuj plik";
    progressBar.classList.remove("progress-bar--active");
}

function appendLog(msg) {
    if (!logsArea) {
        logsArea = document.querySelector("textarea");
    }
    const line = msg == null ? "" : String(msg);
    logsArea.value += `${line}\n`;
    logsArea.scrollTop = logsArea.scrollHeight;
}

function onPipelineDone(result) {
    setButtonState("success");

    const total = result && result.records_count != null ? result.records_count : 0;
    const noPrice = result && result.records_without_price != null ? result.records_without_price : 0;
    const noFacility = result && result.records_without_facility != null ? result.records_without_facility : 0;
    const outputPath = result && result.output_file_path ? result.output_file_path : "";

    appendLog(`Rekord\u00f3w: ${total} | Bez ceny: ${noPrice} | Bez plac\u00f3wki: ${noFacility} | Plik: ${outputPath}`);
}

function onPipelineError(err) {
    setButtonState("error");
    appendLog("B\u0141\u0104D PIPELINE:");
    appendLog(err);
}

function clearInputErrors() {
    Object.values(fieldToInput).forEach(input => input.classList.remove("input--error"));
}

function markInputErrors(errors) {
    errors.forEach(error => {
        const field = error && error.field ? String(error.field) : "";
        const input = fieldToInput[field];
        if (input) {
            input.classList.add("input--error");
        }
    });
}

function setPreviewButtonLoading(isLoading) {
    if (!previewButton) {
        return;
    }
    previewButton.disabled = isLoading;
    previewButton.textContent = isLoading ? "\u0141adowanie..." : "Podgl\u0105d";
}

function renderPreviewTable(previewData) {
    const columns = Array.isArray(previewData.columns) ? previewData.columns : [];
    const rows = Array.isArray(previewData.rows) ? previewData.rows : [];
    const total = previewData && previewData.total != null ? previewData.total : 0;
    const withoutPrice = previewData && previewData.without_price != null ? previewData.without_price : 0;
    const withoutFacility = previewData && previewData.without_facility != null ? previewData.without_facility : 0;

    previewSummary.textContent = `\u0141\u0105cznie rekord\u00f3w: ${total} | Bez ceny: ${withoutPrice} | Bez plac\u00f3wki: ${withoutFacility}`;

    previewHead.innerHTML = "";
    previewBody.innerHTML = "";

    const headerRow = document.createElement("tr");
    columns.forEach(column => {
        const th = document.createElement("th");
        th.textContent = column == null ? "" : String(column);
        headerRow.appendChild(th);
    });
    previewHead.appendChild(headerRow);

    rows.forEach(row => {
        const tr = document.createElement("tr");
        const rowData = Array.isArray(row) ? row : [];

        columns.forEach((_, index) => {
            const td = document.createElement("td");
            const value = index < rowData.length ? rowData[index] : "";
            td.textContent = value == null ? "" : String(value);
            tr.appendChild(td);
        });

        previewBody.appendChild(tr);
    });

    previewSection.style.display = "block";
}

window.appendLog = appendLog;
window.onPipelineDone = onPipelineDone;
window.onPipelineError = onPipelineError;

window.addEventListener("pywebviewready", () => {
    const rows = document.querySelectorAll(".form-row");

    orderInput = document.getElementById("order-file");
    cennikInput = document.getElementById("price-file");
    placowkiInput = document.getElementById("facility-file");
    templateInput = document.getElementById("template-file");
    outputInput = document.getElementById("output-folder");
    dateInput = document.getElementById("delivery-date");
    statusLabel = document.querySelector(".status");
    logsArea = document.querySelector("textarea");
    generateButton = document.querySelector(".btn-primary");
    previewButton = document.getElementById("preview-button");
    progressBar = document.getElementById("progress-bar");
    previewSection = document.getElementById("preview-section");
    previewSummary = document.getElementById("preview-summary");
    previewHead = document.getElementById("preview-head");
    previewBody = document.getElementById("preview-body");
    setButtonState("default");

    fieldToInput = {
        order: orderInput,
        cennik: cennikInput,
        placowki: placowkiInput,
        template: templateInput,
        output: outputInput,
        date: dateInput,
    };

    Object.values(fieldToInput).forEach(input => {
        input.addEventListener("input", () => {
            input.classList.remove("input--error");
        });
    });

    window.pywebview.api.get_defaults().then(defaults => {
        if (defaults.cennik) cennikInput.value = defaults.cennik;
        if (defaults.placowki) placowkiInput.value = defaults.placowki;
        if (defaults.template) templateInput.value = defaults.template;
    });

    const orderPickButton = rows[0].querySelector("button");
    const cennikPickButton = rows[1].querySelector("button");
    const placowkiPickButton = rows[2].querySelector("button");
    const templatePickButton = rows[3].querySelector("button");
    const outputPickButton = rows[4].querySelector("button");

    orderPickButton.addEventListener("click", async () => {
        const path = await window.pywebview.api.pick_file(["Excel Files (*.xlsx;*.xls)", "*.*"]);
        if (path) {
            orderInput.value = path;
        }
    });

    cennikPickButton.addEventListener("click", async () => {
        const path = await window.pywebview.api.pick_file(["Excel Files (*.xlsx;*.xls)", "*.*"]);
        if (path) {
            cennikInput.value = path;
        }
    });

    placowkiPickButton.addEventListener("click", async () => {
        const path = await window.pywebview.api.pick_file(["Excel Files (*.xlsx;*.xls)", "*.*"]);
        if (path) {
            placowkiInput.value = path;
        }
    });

    templatePickButton.addEventListener("click", async () => {
        const path = await window.pywebview.api.pick_file(["Excel Files (*.xlsx;*.xls)", "*.*"]);
        if (path) {
            templateInput.value = path;
        }
    });

    outputPickButton.addEventListener("click", async () => {
        const path = await window.pywebview.api.pick_folder();
        if (path) {
            outputInput.value = path;
        }
    });

    previewButton.addEventListener("click", async () => {
        const order = orderInput.value.trim();
        const cennik = cennikInput.value.trim();
        const placowki = placowkiInput.value.trim();
        const template = templateInput.value.trim();
        const outputDir = outputInput.value.trim();
        const date = dateInput.value.trim();

        clearInputErrors();

        const validationErrors = await window.pywebview.api.validate_inputs(
            order,
            cennik,
            placowki,
            template,
            outputDir,
            date
        );

        if (Array.isArray(validationErrors) && validationErrors.length > 0) {
            validationErrors.forEach(error => {
                const message = error && error.message ? String(error.message) : "Nieznany b\u0142\u0105d walidacji.";
                appendLog(`\u274c ${message}`);
            });
            markInputErrors(validationErrors);
            return;
        }

        setPreviewButtonLoading(true);
        try {
            const previewData = await window.pywebview.api.get_preview(order, cennik, placowki, template, date);
            if (previewData && previewData.error) {
                appendLog(`B\u0141\u0104D PODGL\u0104DU: ${String(previewData.error)}`);
                return;
            }
            renderPreviewTable(previewData || {});
        } catch (err) {
            appendLog(`B\u0141\u0104D PODGL\u0104DU: ${String(err)}`);
        } finally {
            setPreviewButtonLoading(false);
        }
    });

    generateButton.addEventListener("click", async () => {
        const order = orderInput.value.trim();
        const cennik = cennikInput.value.trim();
        const placowki = placowkiInput.value.trim();
        const template = templateInput.value.trim();
        const outputDir = outputInput.value.trim();
        const date = dateInput.value.trim();

        clearInputErrors();

        const validationErrors = await window.pywebview.api.validate_inputs(
            order,
            cennik,
            placowki,
            template,
            outputDir,
            date
        );

        if (Array.isArray(validationErrors) && validationErrors.length > 0) {
            validationErrors.forEach(error => {
                const message = error && error.message ? String(error.message) : "Nieznany b\u0142\u0105d walidacji.";
                appendLog(`\u274c ${message}`);
            });
            markInputErrors(validationErrors);
            return;
        }

        statusLabel.textContent = "Status: Przetwarzanie...";
        setButtonState("loading");
        appendLog("Start pipeline...");

        try {
            await window.pywebview.api.run_pipeline(order, cennik, placowki, template, outputDir, date);
        } catch (err) {
            onPipelineError(String(err));
        }
    });
});