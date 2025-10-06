// Configuration
const API_URL = 'https://k-map-simplifier.vercel.app/api';

// State
let currentMode = 'SOP';
let currentNumVars = 3;

// DOM Elements
const numVarsSelect = document.getElementById('numVars');
const mintermsInput = document.getElementById('minterms');
const dontCaresInput = document.getElementById('dontcares');
const simplifyBtn = document.getElementById('simplifyBtn');
const clearBtn = document.getElementById('clearBtn');
const resultCard = document.getElementById('resultCard');
const tabs = document.querySelectorAll('.tab');
const termsLabel = document.getElementById('termsLabel');
const rangeText = document.getElementById('rangeText');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    updateRangeText();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentMode = tab.dataset.mode;
            termsLabel.textContent = currentMode === 'SOP' ? 'Minterms' : 'Maxterms';
        });
    });

    numVarsSelect.addEventListener('change', (e) => {
        currentNumVars = parseInt(e.target.value);
        updateRangeText();
    });

    simplifyBtn.addEventListener('click', handleSimplify);
    clearBtn.addEventListener('click', handleClear);
}

function updateRangeText() {
    const maxTerm = Math.pow(2, currentNumVars) - 1;
    rangeText.textContent = `0 to ${maxTerm}`;
}

// Parse comma-separated terms
function parseTerms(input) {
    if (!input.trim()) return [];
    return input
        .split(',')
        .map(s => s.trim())
        .filter(s => s.length > 0)
        .map(s => parseInt(s, 10))
        .filter(n => !isNaN(n));
}

// Show toast notification
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Validate inputs
function validateInputs(minterms, dontCares) {
    const maxTerm = Math.pow(2, currentNumVars) - 1;
    const allTerms = [...minterms, ...dontCares];

    if (minterms.length === 0) {
        showToast('Please enter at least one term', 'error');
        return false;
    }

    for (const term of allTerms) {
        if (term < 0 || term > maxTerm) {
            showToast(`Term ${term} is out of range. Valid range: 0-${maxTerm}`, 'error');
            return false;
        }
    }

    if (new Set(allTerms).size !== allTerms.length) {
        showToast('Duplicate terms found', 'error');
        return false;
    }

    return true;
}

// Display result
function displayResult(data) {
    document.getElementById('resultExpression').textContent = data.simplified;
    document.getElementById('resultVars').textContent = data.variables.join(', ');
    document.getElementById('resultMode').textContent = data.mode;
    document.getElementById('resultTerms').textContent = data.original_terms.join(', ');

    const dontCaresBox = document.getElementById('dontCaresBox');
    if (data.dont_cares && data.dont_cares.length > 0) {
        document.getElementById('resultDontCares').textContent = data.dont_cares.join(', ');
        dontCaresBox.style.display = 'block';
    } else {
        dontCaresBox.style.display = 'none';
    }

    resultCard.style.display = 'block';
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Handle simplify
async function handleSimplify() {
    const minterms = parseTerms(mintermsInput.value);
    const dontCares = parseTerms(dontCaresInput.value);

    if (!validateInputs(minterms, dontCares)) {
        return;
    }

    simplifyBtn.disabled = true;
    simplifyBtn.textContent = '⏳ Processing...';

    try {
        const response = await fetch(`${API_URL}/simplify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                minterms: minterms,
                num_vars: currentNumVars,
                mode: currentMode,
                dont_cares: dontCares
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Simplification failed');
        }

        displayResult(data);
        showToast('Expression simplified successfully!', 'success');
    } catch (error) {
        showToast(error.message || 'Failed to connect to server', 'error');
        console.error('Error:', error);
    } finally {
        simplifyBtn.disabled = false;
        simplifyBtn.textContent = '⚡ Simplify Expression';
    }
}

// Handle clear
function handleClear() {
    mintermsInput.value = '';
    dontCaresInput.value = '';
    resultCard.style.display = 'none';
}
