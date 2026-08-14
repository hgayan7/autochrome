// Autochrome Master Photographic Darkroom UI Controller

const liveImg = document.getElementById('liveImage');
const origImg = document.getElementById('originalImage');
const splitCurtain = document.getElementById('splitCurtain');
const splitClipper = document.getElementById('splitClipper');
const splitDivider = document.getElementById('splitDivider');
const splitOriginalImage = document.getElementById('splitOriginalImage');

const agentState = document.getElementById('agentState');
const actionDesc = document.getElementById('actionDesc');
const dimVal = document.getElementById('dimVal');
const actionCountVal = document.getElementById('actionCountVal');

const btnHold = document.getElementById('btnHoldCompare');
const btnSplit = document.getElementById('btnSplitToggle');
const btnHistogram = document.getElementById('btnHistogramToggle');
const btnGrid = document.getElementById('btnGridToggle');
const btnFit = document.getElementById('btnFit');

const scopesHud = document.getElementById('scopesHud');
const histogramCanvas = document.getElementById('histogramCanvas');
const histCtx = histogramCanvas.getContext('2d');

const gridOverlay = document.getElementById('gridOverlay');
const canvasWrapper = document.getElementById('canvasWrapper');
const viewport = document.getElementById('viewport');

const pixelInspector = document.getElementById('pixelInspector');
const inspectorSwatch = document.getElementById('inspectorSwatch');
const inspectorCoords = document.getElementById('inspectorCoords');
const inspectorHex = document.getElementById('inspectorHex');
const inspectorRGB = document.getElementById('inspectorRGB');

// State
let isComparing = false;
let isSplitMode = false;
let isDraggingSplit = false;
let splitPercent = 50.0;
let showScopes = true;
let showGrid = false;

let scale = 1.0;
let translateX = 0;
let translateY = 0;
let isPanning = false;
let panStartX, panStartY;

let lastVersion = -1;

// Hidden analysis canvas for pixel inspector & histogram
const analysisCanvas = document.createElement('canvas');
const analysisCtx = analysisCanvas.getContext('2d', { willReadFrequently: true });

function applyUpdate(data) {
    if (!data) return;
    if (data.version !== undefined && data.version <= lastVersion && lastVersion !== -1) {
        return;
    }
    if (data.version !== undefined) {
        lastVersion = data.version;
    }

    if (data.image_b64) {
        const src = `data:image/jpeg;base64,${data.image_b64}`;
        liveImg.src = src;
        liveImg.style.display = "block";
        
        // Update analysis canvas when image loads
        const temp = new Image();
        temp.onload = () => {
            analysisCanvas.width = temp.naturalWidth;
            analysisCanvas.height = temp.naturalHeight;
            analysisCtx.drawImage(temp, 0, 0);
            renderHistogram();
            syncSplitImageDimensions();
        };
        temp.src = src;
    }

    if (data.original_b64) {
        const origSrc = `data:image/jpeg;base64,${data.original_b64}`;
        origImg.src = origSrc;
        splitOriginalImage.src = origSrc;
    }

    if (data.description) {
        actionDesc.textContent = data.description;
        agentState.textContent = "AGENT COMMITTED";
        setTimeout(() => { agentState.textContent = "STUDIO IDLE"; }, 1200);
    }

    if (data.width && data.height) {
        dimVal.textContent = `${data.width} × ${data.height} px`;
    }

    if (data.action_count !== undefined) {
        actionCountVal.textContent = `${data.action_count} Action${data.action_count === 1 ? '' : 's'}`;
    }
}

// --------------------------------------------------------------------------
// Real-time RGB Histogram Rendering
// --------------------------------------------------------------------------
function renderHistogram() {
    if (!analysisCanvas.width || !analysisCanvas.height) return;
    const w = histogramCanvas.width;
    const h = histogramCanvas.height;

    histCtx.clearRect(0, 0, w, h);

    const imgData = analysisCtx.getImageData(0, 0, analysisCanvas.width, analysisCanvas.height);
    const data = imgData.data;
    const step = Math.max(1, Math.floor(data.length / (4 * 20000))); // fast subsample

    const rBins = new Uint32Array(256);
    const gBins = new Uint32Array(256);
    const bBins = new Uint32Array(256);
    const lBins = new Uint32Array(256);

    for (let i = 0; i < data.length; i += 4 * step) {
        const r = data[i];
        const g = data[i + 1];
        const b = data[i + 2];
        const lum = Math.round(0.299 * r + 0.587 * g + 0.114 * b);

        rBins[r]++;
        gBins[g]++;
        bBins[b]++;
        lBins[lum]++;
    }

    let maxBin = 1;
    for (let i = 2; i < 254; i++) { // ignore extreme clipped spikes for clean curve
        if (rBins[i] > maxBin) maxBin = rBins[i];
        if (gBins[i] > maxBin) maxBin = gBins[i];
        if (bBins[i] > maxBin) maxBin = bBins[i];
        if (lBins[i] > maxBin) maxBin = lBins[i];
    }

    function drawChannelCurve(bins, strokeStyle, fillStyle) {
        histCtx.beginPath();
        histCtx.moveTo(0, h);
        for (let i = 0; i < 256; i++) {
            const x = (i / 255.0) * w;
            const normH = (bins[i] / maxBin) * (h - 6);
            const y = h - normH;
            histCtx.lineTo(x, y);
        }
        histCtx.lineTo(w, h);
        histCtx.closePath();

        if (fillStyle) {
            histCtx.fillStyle = fillStyle;
            histCtx.fill();
        }
        histCtx.strokeStyle = strokeStyle;
        histCtx.lineWidth = 1.0;
        histCtx.stroke();
    }

    // Draw channels with composite blend
    histCtx.globalCompositeOperation = 'screen';
    drawChannelCurve(rBins, 'rgba(239, 68, 68, 0.75)', 'rgba(239, 68, 68, 0.12)');
    drawChannelCurve(gBins, 'rgba(16, 185, 129, 0.75)', 'rgba(16, 185, 129, 0.12)');
    drawChannelCurve(bBins, 'rgba(59, 130, 246, 0.75)', 'rgba(59, 130, 246, 0.12)');
    drawChannelCurve(lBins, 'rgba(255, 255, 255, 0.85)', 'rgba(255, 255, 255, 0.08)');
    histCtx.globalCompositeOperation = 'source-over';
}

// --------------------------------------------------------------------------
// Split Curtain Comparison
// --------------------------------------------------------------------------
function setSplitPercent(pct) {
    splitPercent = Math.max(0, Math.min(100, pct));
    splitClipper.style.width = `${splitPercent}%`;
    splitDivider.style.left = `${splitPercent}%`;
    syncSplitImageDimensions();
}

function syncSplitImageDimensions() {
    if (!liveImg.offsetWidth) return;
    splitOriginalImage.style.width = `${liveImg.offsetWidth}px`;
    splitOriginalImage.style.height = `${liveImg.offsetHeight}px`;
}

function toggleSplit() {
    isSplitMode = !isSplitMode;
    if (isSplitMode) {
        splitCurtain.classList.remove('hidden');
        btnSplit.classList.add('active');
        setSplitPercent(50);
    } else {
        splitCurtain.classList.add('hidden');
        btnSplit.classList.remove('active');
    }
}

btnSplit.addEventListener('click', toggleSplit);

splitDivider.addEventListener('mousedown', (e) => {
    e.stopPropagation();
    isDraggingSplit = true;
});

window.addEventListener('mousemove', (e) => {
    if (isDraggingSplit && isSplitMode) {
        const rect = canvasWrapper.getBoundingClientRect();
        const pct = ((e.clientX - rect.left) / rect.width) * 100.0;
        setSplitPercent(pct);
    }
});

window.addEventListener('mouseup', () => {
    isDraggingSplit = false;
});

// --------------------------------------------------------------------------
// Hold to Compare Original
// --------------------------------------------------------------------------
function startCompare() {
    if (!isComparing && origImg.src) {
        isComparing = true;
        origImg.classList.remove('hidden');
        btnHold.classList.add('active');
        agentState.textContent = "VIEWING REFERENCE";
    }
}

function stopCompare() {
    if (isComparing) {
        isComparing = false;
        origImg.classList.add('hidden');
        btnHold.classList.remove('active');
        agentState.textContent = "STUDIO IDLE";
    }
}

btnHold.addEventListener('mousedown', startCompare);
btnHold.addEventListener('mouseup', stopCompare);
btnHold.addEventListener('mouseleave', stopCompare);

// --------------------------------------------------------------------------
// Scopes, Co-Pilot & Grid Toggles
// --------------------------------------------------------------------------
const btnCopilot = document.getElementById('btnCopilotToggle');
const copilotDrawer = document.getElementById('copilotDrawer');
const btnResetCopilot = document.getElementById('btnResetCopilot');
const btnApplyCopilot = document.getElementById('btnApplyCopilot');

let showCopilot = false;

if (btnCopilot && copilotDrawer) {
    btnCopilot.addEventListener('click', () => {
        showCopilot = !showCopilot;
        copilotDrawer.classList.toggle('hidden', !showCopilot);
        btnCopilot.classList.toggle('active', showCopilot);
    });
}

// Live slider values display
const sliders = ['Exposure', 'Contrast', 'Ambiance', 'Warmth', 'Saturation', 'Structure'];
sliders.forEach(name => {
    const s = document.getElementById(`slider${name}`);
    const v = document.getElementById(`val${name}`);
    if (s && v) {
        s.addEventListener('input', () => {
            v.textContent = (s.value > 0 ? '+' : '') + s.value;
        });
    }
});

if (btnResetCopilot) {
    btnResetCopilot.addEventListener('click', () => {
        sliders.forEach(name => {
            const s = document.getElementById(`slider${name}`);
            const v = document.getElementById(`val${name}`);
            if (s && v) {
                s.value = 0;
                v.textContent = '0';
            }
        });
    });
}

if (btnApplyCopilot) {
    btnApplyCopilot.addEventListener('click', () => {
        const exp = parseFloat(document.getElementById('sliderExposure').value) || 0;
        const con = parseFloat(document.getElementById('sliderContrast').value) || 0;
        const amb = parseFloat(document.getElementById('sliderAmbiance').value) || 0;
        const wrm = parseFloat(document.getElementById('sliderWarmth').value) || 0;
        const sat = parseFloat(document.getElementById('sliderSaturation').value) || 0;
        const str = parseFloat(document.getElementById('sliderStructure').value) || 0;

        btnApplyCopilot.textContent = 'COMMITTING...';

        fetch('/api/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                tool: 'tune_image',
                args: { brightness: exp, contrast: con, ambiance: amb, warmth: wrm, saturation: sat }
            })
        })
        .then(() => {
            if (str !== 0) {
                return fetch('/api/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        tool: 'adjust_details',
                        args: { structure: str, sharpening: str * 0.5 }
                    })
                });
            }
        })
        .then(() => {
            btnApplyCopilot.textContent = 'COMMITTED!';
            setTimeout(() => { btnApplyCopilot.textContent = 'COMMIT TO CANVAS'; }, 1000);
        })
        .catch(err => {
            console.error(err);
            btnApplyCopilot.textContent = 'COMMIT FAILED';
            setTimeout(() => { btnApplyCopilot.textContent = 'COMMIT TO CANVAS'; }, 1000);
        });
    });
}

btnHistogram.addEventListener('click', () => {
    showScopes = !showScopes;
    scopesHud.style.display = showScopes ? 'block' : 'none';
    btnHistogram.classList.toggle('active', showScopes);
});

btnGrid.addEventListener('click', () => {
    showGrid = !showGrid;
    gridOverlay.classList.toggle('hidden', !showGrid);
    btnGrid.classList.toggle('active', showGrid);
});

// --------------------------------------------------------------------------
// Pixel Inspector Hover
// --------------------------------------------------------------------------
canvasWrapper.addEventListener('mousemove', (e) => {
    if (!analysisCanvas.width || isPanning) return;
    const rect = liveImg.getBoundingClientRect();
    if (e.clientX < rect.left || e.clientX > rect.right || e.clientY < rect.top || e.clientY > rect.bottom) return;

    const normX = (e.clientX - rect.left) / rect.width;
    const normY = (e.clientY - rect.top) / rect.height;

    const px = Math.floor(normX * analysisCanvas.width);
    const py = Math.floor(normY * analysisCanvas.height);

    if (px >= 0 && px < analysisCanvas.width && py >= 0 && py < analysisCanvas.height) {
        const pixel = analysisCtx.getImageData(px, py, 1, 1).data;
        const r = pixel[0], g = pixel[1], b = pixel[2];
        const hex = `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase()}`;

        inspectorSwatch.style.backgroundColor = `rgb(${r},${g},${b})`;
        inspectorCoords.textContent = `${px}, ${py}`;
        inspectorHex.textContent = hex;
        inspectorRGB.textContent = `${r}, ${g}, ${b}`;
    }
});

// --------------------------------------------------------------------------
// Viewport Zoom & Pan
// --------------------------------------------------------------------------
viewport.addEventListener('wheel', (e) => {
    e.preventDefault();
    const factor = e.deltaY < 0 ? 1.08 : 0.92;
    scale = Math.min(Math.max(0.25, scale * factor), 6.0);
    updateTransform();
}, { passive: false });

viewport.addEventListener('mousedown', (e) => {
    if (e.target === viewport || e.target === liveImg || e.target === origImg) {
        isPanning = true;
        panStartX = e.clientX - translateX;
        panStartY = e.clientY - translateY;
    }
});

window.addEventListener('mousemove', (e) => {
    if (isPanning) {
        translateX = e.clientX - panStartX;
        translateY = e.clientY - panStartY;
        updateTransform();
    }
});

window.addEventListener('mouseup', () => {
    isPanning = false;
});

btnFit.addEventListener('click', () => {
    scale = 1.0;
    translateX = 0;
    translateY = 0;
    updateTransform();
});

function updateTransform() {
    canvasWrapper.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
}

// --------------------------------------------------------------------------
// Keyboard Shortcuts
// --------------------------------------------------------------------------
window.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

    if (e.code === 'Space' && !e.repeat) {
        e.preventDefault();
        startCompare();
    } else if (e.key === 's' || e.key === 'S') {
        toggleSplit();
    } else if (e.key === 'c' || e.key === 'C') {
        if (btnCopilot) btnCopilot.click();
    } else if (e.key === 'h' || e.key === 'H') {
        btnHistogram.click();
    } else if (e.key === 'g' || e.key === 'G') {
        btnGrid.click();
    } else if (e.key === '0') {
        btnFit.click();
    }
});

window.addEventListener('keyup', (e) => {
    if (e.code === 'Space') {
        e.preventDefault();
        stopCompare();
    }
});

// --------------------------------------------------------------------------
// High Frequency WebSocket + 350ms Polling Heartbeat
// --------------------------------------------------------------------------
function pollState() {
    fetch('/api/state')
        .then(res => res.json())
        .then(data => {
            if (data && data.image_b64) applyUpdate(data);
        })
        .catch(() => {});
}

pollState();
setInterval(pollState, 350);

function connectWS() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    let socket;
    try {
        socket = new WebSocket(wsUrl);
    } catch(e) {
        return;
    }

    socket.onopen = () => {
        agentState.textContent = "STUDIO CONNECTED";
        setTimeout(() => { agentState.textContent = "STUDIO IDLE"; }, 1500);
    };

    socket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.type === "update") applyUpdate(data);
        } catch (err) {
            console.error("WS parse error:", err);
        }
    };

    socket.onclose = () => {
        agentState.textContent = "OFFLINE SYNC";
        setTimeout(connectWS, 1500);
    };
}

connectWS();
