const apiBaseUrl = "http://127.0.0.1:8000";

function getToken() {
    return localStorage.getItem("oncoai_token");
}

function setLoading(button, isLoading) {
    if (isLoading) {
        button.disabled = true;
        button.innerHTML = '<span class="loading"></span> Procesando...';
    } else {
        button.disabled = false;
        button.innerHTML = button.getAttribute('data-original-text') || 'Enviar';
    }
}

function showResult(elementId, message, type = 'info') {
    const element = document.getElementById(elementId);
    if (!element) return;
    element.innerHTML = message;
    element.className = `result ${type}`;
    element.style.display = 'block';
}

function clearResult(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    element.innerHTML = '';
    element.style.display = 'none';
    element.className = 'result';
}

function setLoading(button, isLoading) {
    if (isLoading) {
        button.disabled = true;
        button.innerHTML = '<span class="loading"></span> Procesando...';
    } else {
        button.disabled = false;
        button.innerHTML = button.getAttribute('data-original-text') || 'Enviar';
    }
}


const genes = [
    "B2M", "C1QB", "C1QC", "CASP1", "CD2", "CD3E", "CD4", "CD74",
    "FCER1G", "FCGR3A", "IL10", "LCK", "LCP2", "LYN", "PTPRC", "SERPING1"
];

function createInputFields() {
    const fieldsContainer = document.getElementById("fieldsContainer");
    fieldsContainer.innerHTML = '';

    // Crear tabla
    const table = document.createElement('table');
    table.className = 'input-table';

    // Crear encabezados
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    ['Gen', 'Expresión', 'SCNA'].forEach(text => {
        const th = document.createElement('th');
        th.textContent = text;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Crear cuerpo de tabla
    const tbody = document.createElement('tbody');

    genes.forEach(gene => {
        const tr = document.createElement('tr');

        // Columna 1: nombre del gen
        const tdGene = document.createElement('td');
        tdGene.textContent = gene;
        tr.appendChild(tdGene);

        // Columna 2: input de expresión
        const tdExpr = document.createElement('td');
        const inputExpr = document.createElement('input');
        inputExpr.type = 'number';
        inputExpr.step = 'any';
        inputExpr.name = `${gene}_expression`;
        inputExpr.required = true;
        inputExpr.value = 0;
        inputExpr.placeholder = '0.0';
        inputExpr.className = 'form-input';
        tdExpr.appendChild(inputExpr);
        tr.appendChild(tdExpr);

        // Columna 3: input de SCNA
        const tdScna = document.createElement('td');
        const inputScna = document.createElement('input');
        inputScna.type = 'number';
        inputScna.step = 'any';
        inputScna.name = `${gene}_scna`;
        inputScna.required = true;
        inputScna.value = 0;
        inputScna.placeholder = '0.0';
        inputScna.className = 'form-input';
        tdScna.appendChild(inputScna);
        tr.appendChild(tdScna);

        tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    fieldsContainer.appendChild(table);
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

        console.log('Archivo enviado:', fileInput.files[0]);
        for (const pair of formData.entries()) {
            console.log(pair[0] + ':', pair[1]);
        }

        const response = await fetch(`${apiBaseUrl}/api/predict/batch_predict`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`
                // No set Content-Type; browser will set multipart/form-data
            },
            body: formData
        });

        console.log('Status respuesta:', response.status);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error('Error en respuesta:', errorData);
            throw new Error(errorData.detail || 'Error en la predicción batch');
        }

        const data = await response.json();

        displayBatchResults(data.predictions);

    } catch (error) {
        console.error(error);
        showResult('batchResult', `❌ Error: ${error.message}`, 'error');
    } finally {
        setLoading(button, false);
    }
}

function displayBatchResults(predictions) {
    const container = document.getElementById('batchResult');
    if (!container) return;

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
    container.style.display = 'block';
}

function showSection(section) {
    const sections = ['manual', 'batch'];
    sections.forEach(sec => {
        const element = document.getElementById(`${sec}-section`);
        if (element) {
            element.style.display = sec === section ? 'block' : 'none';
        }
    });
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
