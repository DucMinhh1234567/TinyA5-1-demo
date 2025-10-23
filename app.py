"""
Flask Backend for TinyA5/1 Web Visualizer
Provides REST API endpoints for encryption/decryption with step-by-step visualization.
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from tinya51 import TinyA51, char_to_binary, binary_to_char, validate_key, validate_binary_data, validate_char_data
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for local development


@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template('index.html')


@app.route('/api/encrypt', methods=['POST'])
def encrypt():
    """Encrypt plaintext using TinyA5/1."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'plaintext' not in data or 'key' not in data:
            return jsonify({'error': 'Missing required fields: plaintext, key'}), 400
        
        plaintext = data['plaintext']
        key = data['key']
        input_format = data.get('input_format', 'binary')  # 'binary' or 'char'
        verbose = data.get('verbose', False)
        
        # Validate key
        valid_key, key_msg = validate_key(key)
        if not valid_key:
            return jsonify({'error': f'Key validation failed: {key_msg}'}), 400
        
        # Validate and convert data
        if input_format == 'char':
            valid_data, data_msg = validate_char_data(plaintext)
            if not valid_data:
                return jsonify({'error': f'Data validation failed: {data_msg}'}), 400
            try:
                binary_data = char_to_binary(plaintext)
            except ValueError as e:
                return jsonify({'error': f'Character conversion failed: {e}'}), 400
        else:
            valid_data, data_msg = validate_binary_data(plaintext)
            if not valid_data:
                return jsonify({'error': f'Data validation failed: {data_msg}'}), 400
            binary_data = plaintext
        
        # Perform encryption
        cipher = TinyA51(key)
        result = cipher.encrypt_decrypt(binary_data, verbose=verbose)
        
        # Prepare response
        response = {
            'success': True,
            'plaintext': plaintext,
            'plaintext_binary': binary_data,
            'ciphertext': result['result'],
            'key': key,
            'input_format': input_format
        }
        
        # Add character representation if possible
        if input_format == 'char':
            try:
                response['ciphertext_char'] = binary_to_char(result['result'])
            except ValueError:
                response['ciphertext_char'] = None
        
        # Add step-by-step information if requested
        if verbose:
            response['steps'] = result['steps']
            response['initial_state'] = {
                'X': cipher.X.copy(),
                'Y': cipher.Y.copy(),
                'Z': cipher.Z.copy()
            }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': f'Encryption failed: {str(e)}'}), 500


@app.route('/api/decrypt', methods=['POST'])
def decrypt():
    """Decrypt ciphertext using TinyA5/1."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'ciphertext' not in data or 'key' not in data:
            return jsonify({'error': 'Missing required fields: ciphertext, key'}), 400
        
        ciphertext = data['ciphertext']
        key = data['key']
        input_format = data.get('input_format', 'binary')  # 'binary' or 'char'
        verbose = data.get('verbose', False)
        
        # Validate key
        valid_key, key_msg = validate_key(key)
        if not valid_key:
            return jsonify({'error': f'Key validation failed: {key_msg}'}), 400
        
        # Validate and convert data
        if input_format == 'char':
            valid_data, data_msg = validate_char_data(ciphertext)
            if not valid_data:
                return jsonify({'error': f'Data validation failed: {data_msg}'}), 400
            try:
                binary_data = char_to_binary(ciphertext)
            except ValueError as e:
                return jsonify({'error': f'Character conversion failed: {e}'}), 400
        else:
            valid_data, data_msg = validate_binary_data(ciphertext)
            if not valid_data:
                return jsonify({'error': f'Data validation failed: {data_msg}'}), 400
            binary_data = ciphertext
        
        # Perform decryption (same as encryption for stream cipher)
        cipher = TinyA51(key)
        result = cipher.encrypt_decrypt(binary_data, verbose=verbose)
        
        # Prepare response
        response = {
            'success': True,
            'ciphertext': ciphertext,
            'ciphertext_binary': binary_data,
            'plaintext': result['result'],
            'key': key,
            'input_format': input_format
        }
        
        # Add character representation if possible
        if input_format == 'char':
            try:
                response['plaintext_char'] = binary_to_char(result['result'])
            except ValueError:
                response['plaintext_char'] = None
        
        # Add step-by-step information if requested
        if verbose:
            response['steps'] = result['steps']
            response['initial_state'] = {
                'X': cipher.X.copy(),
                'Y': cipher.Y.copy(),
                'Z': cipher.Z.copy()
            }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': f'Decryption failed: {str(e)}'}), 500


@app.route('/api/validate', methods=['POST'])
def validate():
    """Validate input data without processing."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        key = data.get('key', '')
        input_data = data.get('data', '')
        input_format = data.get('input_format', 'binary')
        
        result = {'valid': True, 'errors': []}
        
        # Validate key
        if key:
            valid_key, key_msg = validate_key(key)
            if not valid_key:
                result['valid'] = False
                result['errors'].append(f'Key: {key_msg}')
        
        # Validate data
        if input_data:
            if input_format == 'char':
                valid_data, data_msg = validate_char_data(input_data)
                if not valid_data:
                    result['valid'] = False
                    result['errors'].append(f'Data: {data_msg}')
            else:
                valid_data, data_msg = validate_binary_data(input_data)
                if not valid_data:
                    result['valid'] = False
                    result['errors'].append(f'Data: {data_msg}')
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': f'Validation failed: {str(e)}'}), 500


@app.route('/api/convert', methods=['POST'])
def convert():
    """Convert between binary and character formats."""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data or 'from_format' not in data:
            return jsonify({'error': 'Missing required fields: text, from_format'}), 400
        
        text = data['text']
        from_format = data['from_format']
        
        if from_format == 'char':
            try:
                binary_result = char_to_binary(text)
                return jsonify({
                    'success': True,
                    'original': text,
                    'converted': binary_result,
                    'from_format': 'char',
                    'to_format': 'binary'
                })
            except ValueError as e:
                return jsonify({'error': f'Character to binary conversion failed: {e}'}), 400
        
        elif from_format == 'binary':
            try:
                char_result = binary_to_char(text)
                return jsonify({
                    'success': True,
                    'original': text,
                    'converted': char_result,
                    'from_format': 'binary',
                    'to_format': 'char'
                })
            except ValueError as e:
                return jsonify({'error': f'Binary to character conversion failed: {e}'}), 400
        
        else:
            return jsonify({'error': 'Invalid from_format. Use "char" or "binary"'}), 400
    
    except Exception as e:
        return jsonify({'error': f'Conversion failed: {str(e)}'}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("Starting TinyA5/1 Web Visualizer...")
    print("Open your browser and go to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=5000)
