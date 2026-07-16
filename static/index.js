// Global State
let appData = null;
let activeFilter = 'all';
let activeFilterCond = 'all';
let utilizationChart = null;

// DOM Elements
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('file-input');
const fileInfoBadge = document.getElementById('file-info-badge');
const fileNameText = document.getElementById('file-name-text');
const removeFileBtn = document.getElementById('remove-file-btn');
const actionBar = document.getElementById('action-bar');
const btnProcess = document.getElementById('btn-process');
const loadingOverlay = document.getElementById('loading-overlay');

// Stage toggling elements
const uploadStage = document.getElementById('upload-stage');
const resultsStage = document.getElementById('results-stage');
const btnNewRun = document.getElementById('btn-new-run');

// Metrics elements
const valTotalOs = document.getElementById('val-total-os');
const valZOs = document.getElementById('val-z-os');
const valAOs = document.getElementById('val-a-os');
const valBOs = document.getElementById('val-b-os');
const valCOs = document.getElementById('val-c-os');

// Modal elements
const detailModal = document.getElementById('detail-modal');
const modalCloseBtn = document.getElementById('modal-close-btn');
const modalOsTitle = document.getElementById('modal-os-title');
const modalOsPriorityBadge = document.getElementById('modal-os-priority-badge');
const modalOsDuration = document.getElementById('modal-os-duration');
const modalOsPredecessor = document.getElementById('modal-os-predecessor');
const modalOsCondition = document.getElementById('modal-os-condition');
const modalOsCompletion = document.getElementById('modal-os-completion');
const modalTasksTbody = document.getElementById('modal-tasks-tbody');

// Initialize event listeners
document.addEventListener('DOMContentLoaded', () => {
    setupUploadHandlers();
    setupProcessHandlers();
    setupFilterHandlers();
    setupModalHandlers();
});

// ==========================================================================
// UPLOAD HANDLERS (DRAG & DROP)
// ==========================================================================
function setupUploadHandlers() {
    // Click dropzone to trigger input
    dropzone.addEventListener('click', (e) => {
        // Prevent click if clicking the remove button
        if (e.target === removeFileBtn) return;
        fileInput.click();
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            handleSelectedFile(fileInput.files[0]);
        }
    });

    // Drag-over styling
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('dragover');
        }, false);
    });

    // File drop
    dropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            fileInput.files = files; // Sync input files list
            handleSelectedFile(files[0]);
        }
    });

    // Remove file button
    removeFileBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        resetUpload();
    });
}

function handleSelectedFile(file) {
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
        alert("Por favor, selecione apenas arquivos do Excel (.xlsx ou .xls)");
        resetUpload();
        return;
    }
    
    fileNameText.textContent = file.name;
    fileInfoBadge.style.display = 'flex';
    actionBar.style.display = 'block';
    
    // Hide details during dropzone selection
    dropzone.querySelector('.upload-icon-wrapper').style.display = 'none';
    dropzone.querySelector('.upload-title').style.display = 'none';
    dropzone.querySelector('.upload-description').style.display = 'none';
}

function resetUpload() {
    fileInput.value = '';
    fileInfoBadge.style.display = 'none';
    actionBar.style.display = 'none';
    
    // Restore dropzone texts
    dropzone.querySelector('.upload-icon-wrapper').style.display = 'flex';
    dropzone.querySelector('.upload-title').style.display = 'block';
    dropzone.querySelector('.upload-description').style.display = 'block';
}

// ==========================================================================
// API CLIENT & SOLVER PROCESS
// ==========================================================================
function setupProcessHandlers() {
    btnProcess.addEventListener('click', async () => {
        if (fileInput.files.length === 0) return;
        
        const formData = new FormData();
        formData.append("file", fileInput.files[0]);
        
        // Show loader
        loadingOverlay.style.display = 'flex';
        
        try {
            const response = await fetch('/solve', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || "Erro inesperado do motor de otimização.");
            }
            
            appData = await response.json();
            
            // Hide upload, show results
            uploadStage.style.display = 'none';
            resultsStage.style.display = 'block';
            
            // Render the dashboard
            renderDashboard(appData);
            
        } catch (error) {
            console.error(error);
            alert("Erro ao otimizar o cronograma:\n" + error.message);
        } finally {
            loadingOverlay.style.display = 'none';
        }
    });

    btnNewRun.addEventListener('click', () => {
        // Reset state and views
        appData = null;
        resetUpload();
        resultsStage.style.display = 'none';
        uploadStage.style.display = 'flex';
        
        if (utilizationChart) {
            utilizationChart.destroy();
            utilizationChart = null;
        }
    });
}

// ==========================================================================
// RENDERING DASHBOARD DATA
// ==========================================================================
function renderDashboard(data) {
    // 1. Populate Metrics Cards
    valTotalOs.textContent = data.metrics.n_os;
    valZOs.textContent = data.metrics.n_Z;
    valAOs.textContent = data.metrics.n_A;
    valBOs.textContent = data.metrics.n_B;
    valCOs.textContent = data.metrics.n_C;
    
    // 2. Render Resource HH Progress Bars (Gauges)
    const gaugesContainer = document.getElementById('gauges-container');
    gaugesContainer.innerHTML = '';
    
    const skillsMapping = [
        { pt: 'Mecânico', key: 'mecanico' },
        { pt: 'Elétrico', key: 'eletrico' },
        { pt: 'Lubrificador', key: 'lubrificador' },
        { pt: 'Soldador', key: 'soldador' }
    ];
    
    skillsMapping.forEach(skill => {
        // Compute average utilization percentage across all 5 days
        const values = data.daily_utilization[skill.key];
        const averagePct = Math.round(values.reduce((a, b) => a + b, 0) / values.length);
        
        const gaugeHTML = `
            <div class="gauge-item">
                <div class="gauge-meta">
                    <span class="gauge-name">${skill.pt}</span>
                    <span class="gauge-percentage">${averagePct}%</span>
                </div>
                <div class="gauge-bar-outer">
                    <div class="gauge-bar-inner" style="width: ${averagePct}%"></div>
                </div>
            </div>
        `;
        gaugesContainer.insertAdjacentHTML('beforeend', gaugeHTML);
    });
    
    // 3. Render Weekly Board Columns
    for (let day = 1; day <= 5; day++) {
        const listContainer = document.getElementById(`day-${day}-list`);
        listContainer.innerHTML = '';
        
        const dayOSs = data.schedule[day.toString()] || [];
        
        if (dayOSs.length === 0) {
            listContainer.innerHTML = '<div class="empty-list-info">Nenhuma OS alocada</div>';
            continue;
        }
        
        dayOSs.forEach(osItem => {
            const cardHTML = `
                <div class="os-card prio-${osItem.priority}" data-os-id="${osItem.os}">
                    <div class="card-top">
                        <span class="os-id">${osItem.os}</span>
                        <span class="prio-tag tag-${osItem.priority}">${osItem.priority}</span>
                    </div>
                    <div class="card-details">
                        <span>${osItem.duration}h duração</span>
                        <span class="os-cond-badge">${osItem.condition}</span>
                    </div>
                </div>
            `;
            listContainer.insertAdjacentHTML('beforeend', cardHTML);
        });
    }
    
    // Setup click handlers for all generated OS Cards to open detail modal
    document.querySelectorAll('.os-card').forEach(card => {
        card.addEventListener('click', () => {
            const osId = card.getAttribute('data-os-id');
            openDetailModal(osId);
        });
    });
    
    // 4. Render Chart.js Multi-Bar Daily Utilization
    renderCharts(data);
}

// ==========================================================================
// CHARTS (CHART.JS CONFIGURATION)
// ==========================================================================
function renderCharts(data) {
    const ctx = document.getElementById('utilization-chart').getContext('2d');
    
    if (utilizationChart) {
        utilizationChart.destroy();
    }
    
    // Get style settings from CSS property colors
    const style = getComputedStyle(document.documentElement);
    const textPrimary = style.getPropertyValue('--text-primary').trim() || '#f0f0f3';
    const textMuted = style.getPropertyValue('--text-muted').trim() || '#6e6e77';
    
    const datasets = [
        {
            label: 'Mecânico',
            data: data.daily_utilization.mecanico,
            backgroundColor: style.getPropertyValue('--color-a').trim() || '#3d5a80',
            borderRadius: 6
        },
        {
            label: 'Elétrico',
            data: data.daily_utilization.eletrico,
            backgroundColor: style.getPropertyValue('--color-z').trim() || '#e07a5f',
            borderRadius: 6
        },
        {
            label: 'Lubrificador',
            data: data.daily_utilization.lubrificador,
            backgroundColor: style.getPropertyValue('--color-b').trim() || '#7d9b84',
            borderRadius: 6
        },
        {
            label: 'Soldador',
            data: data.daily_utilization.soldador,
            backgroundColor: style.getPropertyValue('--color-c').trim() || '#6e7e8a',
            borderRadius: 6
        }
    ];
    
    utilizationChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Segunda (D1)', 'Terça (D2)', 'Quarta (D3)', 'Quinta (D4)', 'Sexta (D5)'],
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: textPrimary,
                        padding: 18,
                        font: {
                            family: 'Outfit',
                            size: 12,
                            weight: '500'
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: textMuted,
                        font: {
                            family: 'Outfit',
                            size: 11
                        }
                    }
                },
                y: {
                    max: 110,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                        tickBorderDash: [5, 5]
                    },
                    ticks: {
                        color: textMuted,
                        font: {
                            family: 'Outfit',
                            size: 11
                        },
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

// ==========================================================================
// FILTERS (CARD VISIBILITY FILTERING)
// ==========================================================================
function setupFilterHandlers() {
    // Priority filters
    const filterButtons = document.querySelectorAll('[data-filter]');
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeFilter = btn.getAttribute('data-filter');
            applyFilters();
        });
    });
    
    // Condition filters
    const filterCondButtons = document.querySelectorAll('[data-filter-cond]');
    filterCondButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            filterCondButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeFilterCond = btn.getAttribute('data-filter-cond');
            applyFilters();
        });
    });
}

function applyFilters() {
    const cards = document.querySelectorAll('.os-card');
    
    cards.forEach(card => {
        const osId = card.getAttribute('data-os-id');
        const osData = findOSData(osId);
        
        if (!osData) return;
        
        const matchesPrio = (activeFilter === 'all' || osData.priority === activeFilter);
        const matchesCond = (activeFilterCond === 'all' || osData.condition === activeFilterCond);
        
        if (matchesPrio && matchesCond) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

function findOSData(osId) {
    if (!appData) return null;
    for (let day in appData.schedule) {
        const found = appData.schedule[day].find(item => item.os === osId);
        if (found) return found;
    }
    return null;
}

// ==========================================================================
// MODAL DIALOG (DETAIL SIDE-OVER / OVERLAY)
// ==========================================================================
function setupModalHandlers() {
    modalCloseBtn.addEventListener('click', closeModal);
    
    // Close on click outside container
    detailModal.addEventListener('click', (e) => {
        if (e.target === detailModal) {
            closeModal();
        }
    });
}

function openDetailModal(osId) {
    const osData = findOSData(osId);
    if (!osData) return;
    
    // Set headers
    modalOsTitle.textContent = `Ordem de Serviço: ${osId}`;
    modalOsPriorityBadge.textContent = `Prioridade ${osData.priority}`;
    
    // Reset priority class badge styling
    modalOsPriorityBadge.className = 'modal-eyebrow';
    if (osData.priority === 'Z') modalOsPriorityBadge.style.background = 'rgba(224, 122, 95, 0.15)', modalOsPriorityBadge.style.color = 'var(--color-z)';
    if (osData.priority === 'A') modalOsPriorityBadge.style.background = 'rgba(61, 90, 128, 0.15)', modalOsPriorityBadge.style.color = 'var(--color-a)';
    if (osData.priority === 'B') modalOsPriorityBadge.style.background = 'rgba(125, 155, 132, 0.15)', modalOsPriorityBadge.style.color = 'var(--color-b)';
    if (osData.priority === 'C') modalOsPriorityBadge.style.background = 'rgba(233, 196, 106, 0.15)', modalOsPriorityBadge.style.color = 'var(--color-c)';
    
    // Set stats
    modalOsDuration.textContent = `${osData.duration} horas`;
    modalOsPredecessor.textContent = osData.predecessor || 'Nenhuma';
    modalOsCondition.textContent = osData.condition;
    modalOsCompletion.textContent = `Hora ${osData.end_hour}`;
    
    // Fill task table body
    modalTasksTbody.innerHTML = '';
    osData.tasks.forEach((task, idx) => {
        const rowHTML = `
            <tr>
                <td>Tarefa ${idx + 1} (${task.skill})</td>
                <td>${task.skill}</td>
                <td>${task.duration}h</td>
                <td>${task.quantity}</td>
                <td>${task.duration * task.quantity} HH</td>
            </tr>
        `;
        modalTasksTbody.insertAdjacentHTML('beforeend', rowHTML);
    });
    
    // Show modal
    detailModal.style.display = 'flex';
}

function closeModal() {
    detailModal.style.display = 'none';
}
