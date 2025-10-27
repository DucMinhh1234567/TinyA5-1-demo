/**
 * TinyA5/1 Visualizer Frontend JavaScript
 * Handles UI interactions, API calls, and step-by-step visualization
 */

class TinyA51Visualizer {
    constructor() {
        this.currentSteps = [];
        this.currentStepIndex = 0;
        this.isPlaying = false;
        this.playInterval = null;
        
        this.initializeEventListeners();
        this.updateFormatHints();
    }

    initializeEventListeners() {
        // Option buttons (new button-style selection)
        document.querySelectorAll('.option-btn').forEach(button => {
            button.addEventListener('click', () => this.handleOptionButtonClick(button));
        });

        // Format selection (hidden radio buttons)
        document.querySelectorAll('input[name="input-format"]').forEach(radio => {
            radio.addEventListener('change', () => this.updateFormatHints());
        });

        // Mode selection (hidden radio buttons)
        document.querySelectorAll('input[name="mode"]').forEach(radio => {
            radio.addEventListener('change', () => this.updateMode());
        });

        // Encryption button
        document.getElementById('encrypt-btn').addEventListener('click', () => {
            this.handleEncryption();
        });

        // Decryption button
        document.getElementById('decrypt-btn').addEventListener('click', () => {
            this.handleDecryption();
        });

        // Visualization controls
        document.getElementById('prev-step').addEventListener('click', () => {
            this.previousStep();
        });

        document.getElementById('next-step').addEventListener('click', () => {
            this.nextStep();
        });

        document.getElementById('play-pause').addEventListener('click', () => {
            this.togglePlayPause();
        });

        // Key input validation
        document.querySelectorAll('input[id$="-key"]').forEach(input => {
            input.addEventListener('input', (e) => {
                this.validateKeyInput(e.target);
            });
        });
    }

    handleOptionButtonClick(clickedButton) {
        const group = clickedButton.dataset.group;
        const option = clickedButton.dataset.option;
        
        // Remove active class from all buttons in the same group
        document.querySelectorAll(`.option-btn[data-group="${group}"]`).forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Add active class to clicked button
        clickedButton.classList.add('active');
        
        // Update hidden radio button
        const radio = document.querySelector(`input[name="${group}"][value="${option}"]`);
        if (radio) {
            radio.checked = true;
            radio.dispatchEvent(new Event('change'));
        }
    }

    updateFormatHints() {
        const format = document.querySelector('input[name="input-format"]:checked').value;
        const encryptHint = document.getElementById('encrypt-hint');
        const decryptHint = document.getElementById('decrypt-hint');

        if (format === 'binary') {
            encryptHint.textContent = 'Enter binary string (e.g., "111")';
            decryptHint.textContent = 'Enter binary string (e.g., "011")';
        } else {
            encryptHint.textContent = 'Enter characters A-H (e.g., "H")';
            decryptHint.textContent = 'Enter characters A-H (e.g., "D")';
        }
    }

    updateMode() {
        const mode = document.querySelector('input[name="mode"]:checked').value;
        const visualizationSection = document.getElementById('visualization-section');
        
        if (mode === 'visualize') {
            visualizationSection.style.display = 'block';
        } else {
            visualizationSection.style.display = 'none';
            this.stopPlayback();
        }
    }

    validateKeyInput(input) {
        const value = input.value;
        const isValid = /^[01]*$/.test(value) && value.length <= 23;
        
        if (value.length > 0 && !isValid) {
            input.style.borderColor = '#dc3545';
        } else if (value.length === 23) {
            input.style.borderColor = '#28a745';
        } else {
            input.style.borderColor = '#e9ecef';
        }
    }

    async handleEncryption() {
        const plaintext = document.getElementById('encrypt-plaintext').value.trim();
        const key = document.getElementById('encrypt-key').value.trim();
        const format = document.querySelector('input[name="input-format"]:checked').value;
        const mode = document.querySelector('input[name="mode"]:checked').value;

        if (!this.validateInputs(plaintext, key)) {
            return;
        }

        this.showLoading('encrypt-result');

        try {
            const response = await fetch('/api/encrypt', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    plaintext: plaintext,
                    key: key,
                    input_format: format,
                    verbose: mode === 'visualize'
                })
            });

            const result = await response.json();
            this.displayResult('encrypt-result', result, 'encrypt');
            
            if (mode === 'visualize' && result.steps) {
                this.startVisualization(result.steps, result.initial_state);
            }
        } catch (error) {
            this.showError('encrypt-result', 'Encryption failed: ' + error.message);
        }
    }

    async handleDecryption() {
        const ciphertext = document.getElementById('decrypt-ciphertext').value.trim();
        const key = document.getElementById('decrypt-key').value.trim();
        const format = document.querySelector('input[name="input-format"]:checked').value;
        const mode = document.querySelector('input[name="mode"]:checked').value;

        if (!this.validateInputs(ciphertext, key)) {
            return;
        }

        this.showLoading('decrypt-result');

        try {
            const response = await fetch('/api/decrypt', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    ciphertext: ciphertext,
                    key: key,
                    input_format: format,
                    verbose: mode === 'visualize'
                })
            });

            const result = await response.json();
            this.displayResult('decrypt-result', result, 'decrypt');
            
            if (mode === 'visualize' && result.steps) {
                this.startVisualization(result.steps, result.initial_state);
            }
        } catch (error) {
            this.showError('decrypt-result', 'Decryption failed: ' + error.message);
        }
    }

    validateInputs(data, key) {
        if (!data || !key) {
            this.showError('encrypt-result', 'Please fill in all fields');
            this.showError('decrypt-result', 'Please fill in all fields');
            return false;
        }

        if (key.length !== 23) {
            this.showError('encrypt-result', 'Key must be exactly 23 bits');
            this.showError('decrypt-result', 'Key must be exactly 23 bits');
            return false;
        }

        if (!/^[01]+$/.test(key)) {
            this.showError('encrypt-result', 'Key must contain only 0s and 1s');
            this.showError('decrypt-result', 'Key must contain only 0s and 1s');
            return false;
        }

        const format = document.querySelector('input[name="input-format"]:checked').value;
        if (format === 'binary' && !/^[01]+$/.test(data)) {
            this.showError('encrypt-result', 'Data must contain only 0s and 1s');
            this.showError('decrypt-result', 'Data must contain only 0s and 1s');
            return false;
        }

        if (format === 'char' && !/^[A-H]+$/i.test(data)) {
            this.showError('encrypt-result', 'Data must contain only characters A-H');
            this.showError('decrypt-result', 'Data must contain only characters A-H');
            return false;
        }

        return true;
    }

    showLoading(elementId) {
        const element = document.getElementById(elementId);
        element.innerHTML = '<div class="loading"></div> Processing...';
        element.className = 'result-area';
    }

    showError(elementId, message) {
        const element = document.getElementById(elementId);
        element.innerHTML = `<strong>Error:</strong> ${message}`;
        element.className = 'result-area error';
    }

    displayResult(elementId, result, operation) {
        const element = document.getElementById(elementId);
        
        if (result.error) {
            this.showError(elementId, result.error);
            return;
        }

        let html = '';
        
        if (operation === 'encrypt') {
            html += `<strong>Encryption Result:</strong><br>`;
            html += `Plaintext: ${result.plaintext}<br>`;
            if (result.input_format === 'char') {
                html += `Plaintext (binary): ${result.plaintext_binary}<br>`;
            }
            html += `Ciphertext (binary): ${result.ciphertext}<br>`;
            if (result.ciphertext_char) {
                html += `Ciphertext (characters): ${result.ciphertext_char}<br>`;
            }
        } else {
            html += `<strong>Decryption Result:</strong><br>`;
            html += `Ciphertext: ${result.ciphertext}<br>`;
            if (result.input_format === 'char') {
                html += `Ciphertext (binary): ${result.ciphertext_binary}<br>`;
            }
            html += `Plaintext (binary): ${result.plaintext}<br>`;
            if (result.plaintext_char) {
                html += `Plaintext (characters): ${result.plaintext_char}<br>`;
            }
        }
        
        html += `Key: ${result.key}`;
        
        element.innerHTML = html;
        element.className = 'result-area success';
    }

    startVisualization(steps, initialState) {
        this.currentSteps = steps;
        this.currentStepIndex = 0;
        this.stopPlayback();
        
        // Set initial register state
        this.updateRegisters(initialState);
        this.updateStepInfo(null);
        this.updateStepCounter();
        
        // Show first step
        if (steps.length > 0) {
            this.showStep(0);
        }
    }

    showStep(stepIndex) {
        if (stepIndex < 0 || stepIndex >= this.currentSteps.length) {
            return;
        }

        const step = this.currentSteps[stepIndex];
        this.currentStepIndex = stepIndex;
        
        // Update registers to show state after rotation
        this.updateRegisters({
            X: step.X_after,
            Y: step.Y_after,
            Z: step.Z_after
        });
        
        // Highlight control bits
        this.highlightControlBits(step);
        
        // Update step information
        this.updateStepInfo(step);
        this.updateStepCounter();
        
        // Highlight rotating registers
        this.highlightRotatingRegisters(step);
    }

    updateRegisters(state) {
        // Update register X
        state.X.forEach((bit, index) => {
            const bitElement = document.querySelector(`#register-x .bit[data-bit="${index}"]`);
            if (bitElement) {
                bitElement.textContent = bit;
                bitElement.classList.remove('active', 'rotating');
            }
        });

        // Update register Y
        state.Y.forEach((bit, index) => {
            const bitElement = document.querySelector(`#register-y .bit[data-bit="${index}"]`);
            if (bitElement) {
                bitElement.textContent = bit;
                bitElement.classList.remove('active', 'rotating');
            }
        });

        // Update register Z
        state.Z.forEach((bit, index) => {
            const bitElement = document.querySelector(`#register-z .bit[data-bit="${index}"]`);
            if (bitElement) {
                bitElement.textContent = bit;
                bitElement.classList.remove('active', 'rotating');
            }
        });
    }

    highlightControlBits(step) {
        // Clear previous highlights
        document.querySelectorAll('.bit').forEach(bit => {
            bit.classList.remove('active');
        });

        // Highlight control bits
        if (step) {
            const x2Element = document.querySelector(`#register-x .bit[data-bit="2"]`);
            const y7Element = document.querySelector(`#register-y .bit[data-bit="7"]`);
            const z8Element = document.querySelector(`#register-z .bit[data-bit="8"]`);
            
            if (x2Element) x2Element.classList.add('active');
            if (y7Element) y7Element.classList.add('active');
            if (z8Element) z8Element.classList.add('active');
        }
    }

    highlightRotatingRegisters(step) {
        // Clear previous rotation highlights
        document.querySelectorAll('.bit').forEach(bit => {
            bit.classList.remove('rotating');
        });

        if (step) {
            // Highlight bits that will be rotated
            if (step.rotate_X) {
                document.querySelectorAll('#register-x .bit').forEach(bit => {
                    bit.classList.add('rotating');
                });
            }
            if (step.rotate_Y) {
                document.querySelectorAll('#register-y .bit').forEach(bit => {
                    bit.classList.add('rotating');
                });
            }
            if (step.rotate_Z) {
                document.querySelectorAll('#register-z .bit').forEach(bit => {
                    bit.classList.add('rotating');
                });
            }
        }
    }

    updateStepInfo(step) {
        if (!step) {
            document.getElementById('control-x2').textContent = '0';
            document.getElementById('control-y7').textContent = '0';
            document.getElementById('control-z8').textContent = '0';
            document.getElementById('majority-result').textContent = 'maj(0,0,0) = 0';
            document.getElementById('rotation-info').textContent = 'No rotations';
            document.getElementById('keystream-info').textContent = 's = X[5] ⊕ Y[7] ⊕ Z[8] = 0';
            document.getElementById('encryption-info').textContent = 'Data ⊕ Keystream = Result';
            return;
        }

        // Update control bits
        document.getElementById('control-x2').textContent = step.x2;
        document.getElementById('control-y7').textContent = step.y7;
        document.getElementById('control-z8').textContent = step.z8;

        // Update majority function
        document.getElementById('majority-result').textContent = 
            `maj(${step.x2}, ${step.y7}, ${step.z8}) = ${step.majority}`;

        // Update rotations
        const rotations = [];
        if (step.rotate_X) rotations.push('X');
        if (step.rotate_Y) rotations.push('Y');
        if (step.rotate_Z) rotations.push('Z');
        
        document.getElementById('rotation-info').textContent = 
            rotations.length > 0 ? `Rotate: ${rotations.join(', ')}` : 'No rotations';

        // Update keystream generation
        document.getElementById('keystream-info').textContent = 
            `s = X[5] ⊕ Y[7] ⊕ Z[8] = ${step.X_after[5]} ⊕ ${step.Y_after[7]} ⊕ ${step.Z_after[8]} = ${step.keystream_bit}`;

        // Update encryption
        document.getElementById('encryption-info').textContent = 
            `${step.data_bit} ⊕ ${step.keystream_bit} = ${step.cipher_bit}`;
    }

    updateStepCounter() {
        const counter = document.getElementById('step-counter');
        counter.textContent = `Step ${this.currentStepIndex + 1} of ${this.currentSteps.length}`;
    }

    previousStep() {
        if (this.currentStepIndex > 0) {
            this.currentStepIndex--;
            this.showStep(this.currentStepIndex);
        }
    }

    nextStep() {
        if (this.currentStepIndex < this.currentSteps.length - 1) {
            this.currentStepIndex++;
            this.showStep(this.currentStepIndex);
        }
    }

    togglePlayPause() {
        if (this.isPlaying) {
            this.stopPlayback();
        } else {
            this.startPlayback();
        }
    }

    startPlayback() {
        this.isPlaying = true;
        document.getElementById('play-pause').textContent = 'Pause';
        
        this.playInterval = setInterval(() => {
            if (this.currentStepIndex < this.currentSteps.length - 1) {
                this.nextStep();
            } else {
                this.stopPlayback();
            }
        }, 1500); // 1.5 seconds per step
    }

    stopPlayback() {
        this.isPlaying = false;
        document.getElementById('play-pause').textContent = 'Play';
        
        if (this.playInterval) {
            clearInterval(this.playInterval);
            this.playInterval = null;
        }
    }
}

// Initialize the visualizer when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new TinyA51Visualizer();
});
