class TinyA51Visualizer {
    constructor() {
        this.currentSteps = [];
        this.currentStepIndex = 0;
        this.currentPhase = 0; // 0: before+control, 1: mark rotating, 2: after
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
            encryptHint.textContent = 'Nhập chuỗi nhị phân (ví dụ: "111")';
            decryptHint.textContent = 'Nhập chuỗi nhị phân (ví dụ: "011")';
        } else {
            encryptHint.textContent = 'Nhập ký tự A-H (ví dụ: "H")';
            decryptHint.textContent = 'Nhập ký tự A-H (ví dụ: "D")';
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
            this.showError('encrypt-result', 'Mã hóa thất bại: ' + error.message);
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
            this.showError('decrypt-result', 'Giải mã thất bại: ' + error.message);
        }
    }

    validateInputs(data, key) {
        if (!data || !key) {
            this.showError('encrypt-result', 'Vui lòng điền đầy đủ các trường');
            this.showError('decrypt-result', 'Vui lòng điền đầy đủ các trường');
            return false;
        }

        if (key.length !== 23) {
            this.showError('encrypt-result', 'Khóa phải chính xác 23 bit');
            this.showError('decrypt-result', 'Khóa phải chính xác 23 bit');
            return false;
        }

        if (!/^[01]+$/.test(key)) {
            this.showError('encrypt-result', 'Khóa chỉ được chứa 0 và 1');
            this.showError('decrypt-result', 'Khóa chỉ được chứa 0 và 1');
            return false;
        }

        const format = document.querySelector('input[name="input-format"]:checked').value;
        if (format === 'binary' && !/^[01]+$/.test(data)) {
            this.showError('encrypt-result', 'Dữ liệu chỉ được chứa 0 và 1');
            this.showError('decrypt-result', 'Dữ liệu chỉ được chứa 0 và 1');
            return false;
        }

        if (format === 'char' && !/^[A-H]+$/i.test(data)) {
            this.showError('encrypt-result', 'Dữ liệu chỉ được chứa ký tự A-H');
            this.showError('decrypt-result', 'Dữ liệu chỉ được chứa ký tự A-H');
            return false;
        }

        return true;
    }

    showLoading(elementId) {
        const element = document.getElementById(elementId);
        element.innerHTML = '<div class="loading"></div> Đang xử lý...';
        element.className = 'result-area';
    }

    showError(elementId, message) {
        const element = document.getElementById(elementId);
        element.innerHTML = `<strong>Lỗi:</strong> ${message}`;
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
            html += `<strong>Kết Quả Mã Hóa:</strong><br>`;
            html += `Plaintext: ${result.plaintext}<br>`;
            if (result.input_format === 'char') {
                html += `Plaintext (nhị phân): ${result.plaintext_binary}<br>`;
            }
            html += `Ciphertext (nhị phân): ${result.ciphertext}<br>`;
            if (result.ciphertext_char) {
                html += `Ciphertext (ký tự): ${result.ciphertext_char}<br>`;
            }
        } else {
            html += `<strong>Kết Quả Giải Mã:</strong><br>`;
            html += `Ciphertext: ${result.ciphertext}<br>`;
            if (result.input_format === 'char') {
                html += `Ciphertext (nhị phân): ${result.ciphertext_binary}<br>`;
            }
            html += `Plaintext (nhị phân): ${result.plaintext}<br>`;
            if (result.plaintext_char) {
                html += `Plaintext (ký tự): ${result.plaintext_char}<br>`;
            }
        }
        
        html += `Khóa: ${result.key}`;
        
        element.innerHTML = html;
        element.className = 'result-area success';
    }

    startVisualization(steps, initialState) {
        this.currentSteps = steps;
        this.currentStepIndex = 0;
        this.currentPhase = 0;
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
        
        // Clear any highlights
        document.querySelectorAll('.bit').forEach(bit => {
            bit.classList.remove('active', 'rotating');
        });

        if (this.currentPhase === 0) {
            // Phase 0: show BEFORE state and control bits
            this.updateRegisters({ X: step.X_before, Y: step.Y_before, Z: step.Z_before });
            this.highlightControlBits(step, true);
        } else if (this.currentPhase === 1) {
            // Phase 1: show BEFORE state and mark rotating registers
            this.updateRegisters({ X: step.X_before, Y: step.Y_before, Z: step.Z_before });
            this.highlightRotatingRegisters(step);
        } else {
            // Phase 2: show AFTER state
            this.updateRegisters({ X: step.X_after, Y: step.Y_after, Z: step.Z_after });
        }

        // Update information
        this.updateStepInfo(step);
        this.updateStepCounter();
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

    highlightControlBits(step, isBefore) {
        // Clear previous highlights
        document.querySelectorAll('.bit').forEach(bit => {
            bit.classList.remove('active');
        });

        if (step) {
            if (isBefore) {
                // BEFORE rotation: x1->1, y3->3, z3->3
                const xEl = document.querySelector('#register-x .bit[data-bit="1"]');
                const yEl = document.querySelector('#register-y .bit[data-bit="3"]');
                const zEl = document.querySelector('#register-z .bit[data-bit="3"]');
                if (xEl) xEl.classList.add('active');
                if (yEl) yEl.classList.add('active');
                if (zEl) zEl.classList.add('active');
            } else {
                // AFTER rotation mapping (not used in this flow but kept for completeness)
                const xIndexAfter = step.rotate_X ? 2 : 1;
                const yIndexAfter = step.rotate_Y ? 4 : 3;
                const zIndexAfter = step.rotate_Z ? 4 : 3;
                const xEl = document.querySelector(`#register-x .bit[data-bit="${xIndexAfter}"]`);
                const yEl = document.querySelector(`#register-y .bit[data-bit="${yIndexAfter}"]`);
                const zEl = document.querySelector(`#register-z .bit[data-bit="${zIndexAfter}"]`);
                if (xEl) xEl.classList.add('active');
                if (yEl) yEl.classList.add('active');
                if (zEl) zEl.classList.add('active');
            }
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
            document.getElementById('control-x1').textContent = '0';
            document.getElementById('control-y3').textContent = '0';
            document.getElementById('control-z3').textContent = '0';
            document.getElementById('majority-result').textContent = 'maj(0,0,0) = 0';
            document.getElementById('rotation-info').textContent = 'Không có xoay';
            document.getElementById('keystream-info').textContent = 's = X[5] ⊕ Y[7] ⊕ Z[8] = 0';
            document.getElementById('encryption-info').textContent = 'Dữ liệu ⊕ Keystream = Kết quả';
            return;
        }

        // Update control bits
        document.getElementById('control-x1').textContent = step.x1;
        document.getElementById('control-y3').textContent = step.y3;
        document.getElementById('control-z3').textContent = step.z3;

        // Update majority function
        document.getElementById('majority-result').textContent = 
            `maj(${step.x1}, ${step.y3}, ${step.z3}) = ${step.majority}`;

        // Update rotations
        const rotations = [];
        if (step.rotate_X) rotations.push('X');
        if (step.rotate_Y) rotations.push('Y');
        if (step.rotate_Z) rotations.push('Z');
        
        if (this.currentPhase === 0) {
            document.getElementById('rotation-info').textContent = 
                rotations.length > 0 ? `Sẽ xoay: ${rotations.join(', ')}` : 'Không xoay';
            document.getElementById('keystream-info').textContent = 'Chưa tính (sẽ tính sau khi xoay)';
            document.getElementById('encryption-info').textContent = 'Chưa tính';
        } else if (this.currentPhase === 1) {
            document.getElementById('rotation-info').textContent = 
                rotations.length > 0 ? `Đánh dấu xoay: ${rotations.join(', ')}` : 'Không xoay';
            document.getElementById('keystream-info').textContent = 'Chưa tính (sẽ tính sau khi xoay)';
            document.getElementById('encryption-info').textContent = 'Chưa tính';
        } else {
            document.getElementById('rotation-info').textContent = 
                rotations.length > 0 ? `Đã xoay: ${rotations.join(', ')}` : 'Không xoay';
            document.getElementById('keystream-info').textContent = 
                `s = X[5] ⊕ Y[7] ⊕ Z[8] = ${step.X_after[5]} ⊕ ${step.Y_after[7]} ⊕ ${step.Z_after[8]} = ${step.keystream_bit}`;
            document.getElementById('encryption-info').textContent = 
                `${step.data_bit} ⊕ ${step.keystream_bit} = ${step.cipher_bit}`;
        }
    }

    updateStepCounter() {
        const counter = document.getElementById('step-counter');
        const phaseText = this.currentPhase === 0 ? 'Bước 0: Trạng thái ban đầu' :
            this.currentPhase === 1 ? 'Bước 1: Đánh dấu xoay' : 'Bước 2: Sau khi xoay';
        counter.textContent = `${phaseText} — bước ${this.currentStepIndex + 1}/${this.currentSteps.length}`;
    }

    previousStep() {
        if (this.currentPhase > 0) {
            this.currentPhase--;
            this.showStep(this.currentStepIndex);
            return;
        }
        if (this.currentStepIndex > 0) {
            this.currentStepIndex--;
            this.currentPhase = 2;
            this.showStep(this.currentStepIndex);
        }
    }

    nextStep() {
        if (this.currentPhase < 2) {
            this.currentPhase++;
            this.showStep(this.currentStepIndex);
            return;
        }
        if (this.currentStepIndex < this.currentSteps.length - 1) {
            this.currentStepIndex++;
            this.currentPhase = 0;
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
        document.getElementById('play-pause').textContent = 'Tạm dừng';
        
        this.playInterval = setInterval(() => {
            if (this.currentPhase < 2) {
                this.nextStep();
            } else if (this.currentStepIndex < this.currentSteps.length - 1) {
                this.nextStep();
            } else {
                this.stopPlayback();
            }
        }, 1500); // 1.5 seconds per step
    }

    stopPlayback() {
        this.isPlaying = false;
        document.getElementById('play-pause').textContent = 'Phát';
        
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
