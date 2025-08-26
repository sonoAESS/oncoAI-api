const apiBaseUrl = "http://127.0.0.1:8000";

const requiredFields = [
    'B2M_expression', 'B2M_scna', 'C1QB_expression', 'C1QB_scna',
    'C1QC_expression', 'C1QC_scna', 'CASP1_expression', 'CASP1_scna',
    'CD2_expression', 'CD2_scna', 'CD3E_expression', 'CD3E_scna',
    'CD4_expression', 'CD4_scna', 'CD74_expression', 'CD74_scna',
    'FCER1G_expression', 'FCER1G_scna', 'FCGR3A_expression', 'FCGR3A_scna',
    'IL10_expression', 'IL10_scna', 'LCK_expression', 'LCK_scna',
    'LCP2_expression', 'LCP2_scna', 'LYN_expression', 'LYN_scna',
    'PTPRC_expression', 'PTPRC_scna', 'SERPING1_expression', 'SERPING1_scna'
];

function createInputFields() {
    const fieldsContainer = document.getElementById("fieldsContainer");
    fieldsContainer.innerHTML = '';

    const rowSize = 2;
    let rowDiv;

    requiredFields.forEach((field, index) => {
        if (index % rowSize === 0) {
            rowDiv = document.createElement("div");
            rowDiv.className = "field-row";
            fieldsContainer.appendChild(rowDiv);
        }

        const div = document.createElement("div");
        div.className = "field-group";

        const label = document.createElement("label");
        label.textContent = field.replace(/_/g, ' ') + ":";
        label.title = field;

        const input = document.createElement("input");
        input.type = "number";
        input.step = "any";
        input.name = field;
        input.required = true;
        input.value = 0;
        input.placeholder = "0.0";
        input.className = "form-input";

        div.appendChild(label);
        div.appendChild(input);
        rowDiv.appendChild(div);
    });
}

async function predictManual(e) {
    e.preventDefault();
    const form = e.target;
    const button = form.querySelector('button[type="submit"]');
    const token = getToken();

    if (!token) {
        showResult('result', '❌ Debes iniciar sesión primero', 'error');
        return;
    }

    setLoading(button, true);
    clearResult('result');

    try {
        const features = requiredFields.map(field => {
            const value = parseFloat(form.querySelector(`[name="${field}"]`).value);
            return isNaN(value) ? 0 : value;
        });

        const response = await fetch(`${apiBaseUrl}/api/predict/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ features })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Error en la predicción');
        }

        const data = await response.json();
        const probability = (data.survival_probability * 100).toFixed(2);

        showResult('result',
            `🎯 Probabilidad de supervivencia > 3 años: <span class="prediction-result">${probability}%</span>`,
            'success'
        );

    } catch (error) {
        showResult('result', `❌ Error: ${error.message}`, 'error');
    } finally {
        setLoading(button, false);
    }
}

async function predictBatch(e) {
    e.preventDefault();
    const form = e.target;
    const button = form.querySelector('button[type="submit"]');
    const token = getToken();
    const fileInput = form.querySelector('#fileInput');

    if (!token) {
        showResult('batchResult', '❌ Debes iniciar sesión primero', 'error');
        return;
    }

    if (fileInput.files.length === 0) {
        showResult('batchResult', '❌ Selecciona un archivo CSV o Excel', 'error');
        return;
    }

    setLoading(button, true);
    clearResult('batchResult');

    try {
        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        const response = await fetch(`${apiBaseUrl}/api/predict/batch_predict`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`
            },
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Error en la predicción batch');
        }

        const data = await response.json();
        displayBatchResults(data.predictions);

    } catch (error) {
        showResult('batchResult', `❌ Error: ${error.message}`, 'error');
    } finally {
        setLoading(button, false);
    }
}

function displayBatchResults(predictions) {
    const container = document.getElementById('batchResult');
    let html = `
        <div class="result success">
            <h4>📊 Resultados de Predicción Batch</h4>
            <div class="batch-results">
    `;

    predictions.forEach((result, index) => {
        const probability = (result.survival_probability * 100).toFixed(2);
        const rowClass = result.survival_probability >= 0.5 ? 'success' : 'error';

        html += `
            <div class="batch-result-item ${rowClass}">
                <strong>Fila ${result.row + 1}:</strong> ${probability}%
            </div>
        `;
    });

    html += `
            </div>
            <div class="mt-2">
                <strong>Total:</strong> ${predictions.length} predicciones procesadas
            </div>
        </div>
    `;

    container.innerHTML = html;
}

function initDashboard() {
    createInputFields();

    setupDashboardEventListeners();
}

function setupDashboardEventListeners() {
    document.getElementById('predictForm').addEventListener('submit', predictManual);
    document.getElementById('batchForm').addEventListener('submit', predictBatch);

    const fileInput = document.getElementById('fileInput');
    const fileLabel = document.querySelector('.file-input-label');

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileLabel.textContent = `📄 ${e.target.files[0].name}`;
        } else {
            fileLabel.textContent = '📁 Seleccionar archivo CSV/Excel';
        }
    });
}

document.addEventListener('DOMContentLoaded', initDashboard);
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Error en la predicción batch');
        }

        const data = await response.json();
        displayBatchResults(data.predictions);

    } catch (error) {
        showResult('batchResult', `❌ Error: ${error.message}`, 'error');
    } finally {
        setLoading(button, false);
    }
}

function displayBatchResults(predictions) {
    const container = document.getElementById('batchResult');
    let html = `
        <div class="result success">
            <h4>📊 Resultados de Predicción Batch</h4>
            <div class="batch-results">
    `;

    predictions.forEach((result) => {
        const probability = (result.survival_probability * 100).toFixed(2);
        const rowClass = result.survival_probability >= 0.5 ? 'success' : 'error';

        html += `
            <div class="batch-result-item ${rowClass}">
                <strong>Fila ${result.row + 1}:</strong> ${probability}%
            </div>
        `;
    });

    html += `
            </div>
            <div class="mt-2">
                <strong>Total:</strong> ${predictions.length} predicciones procesadas
            </div>
        </div>
    `;

    container.innerHTML = html;
}

function initDashboard() {
    createInputFields();
    setupDashboardEventListeners();
    // Mostrar seccion manual por defecto
    showSection('manual');
}

function setupDashboardEventListeners() {
    document.getElementById('predictForm').addEventListener('submit', predictManual);
    document.getElementById('batchForm').addEventListener('submit', predictBatch);

    const fileInput = document.getElementById('fileInput');
    const fileLabel = document.querySelector('.file-input-label');

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileLabel.textContent = `📄 ${e.target.files[0].name}`;
        } else {
            fileLabel.textContent = '📁 Seleccionar archivo CSV/Excel';
        }
    });
}

document.addEventListener('DOMContentLoaded', initDashboard);
