import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from tinya51 import TinyA51, char_to_binary, binary_to_char, validate_key, validate_binary_data, validate_char_data
import json

app = Flask(__name__)
CORS(app)  # Bật CORS cho phát triển local


@app.route('/')
def index():
    """Phục vụ giao diện web chính."""
    return render_template('index.html')


@app.route('/api/encrypt', methods=['POST'])
def encrypt():
    """Mã hóa plaintext bằng TinyA5/1."""
    try:
        data = request.get_json()
        
        # Kiểm tra các trường bắt buộc
        if not data or 'plaintext' not in data or 'key' not in data:
            return jsonify({'error': 'Thiếu các trường bắt buộc: plaintext, key'}), 400
        
        plaintext = data['plaintext']
        key = data['key']
        input_format = data.get('input_format', 'binary')  # 'binary' or 'char'
        verbose = data.get('verbose', False)
        
        # Kiểm tra khóa
        valid_key, key_msg = validate_key(key)
        if not valid_key:
            return jsonify({'error': f'Kiểm tra khóa thất bại: {key_msg}'}), 400
        
        # Kiểm tra và chuyển đổi dữ liệu
        if input_format == 'char':
            valid_data, data_msg = validate_char_data(plaintext)
            if not valid_data:
                return jsonify({'error': f'Kiểm tra dữ liệu thất bại: {data_msg}'}), 400
            try:
                binary_data = char_to_binary(plaintext)
            except ValueError as e:
                return jsonify({'error': f'Chuyển đổi ký tự thất bại: {e}'}), 400
        else:
            valid_data, data_msg = validate_binary_data(plaintext)
            if not valid_data:
                return jsonify({'error': f'Kiểm tra dữ liệu thất bại: {data_msg}'}), 400
            binary_data = plaintext
        
        # Thực hiện mã hóa
        cipher = TinyA51(key)
        result = cipher.encrypt_decrypt(binary_data, verbose=verbose)
        
        # Chuẩn bị phản hồi
        response = {
            'success': True,
            'plaintext': plaintext,
            'plaintext_binary': binary_data,
            'ciphertext': result['result'],
            'key': key,
            'input_format': input_format
        }
        
        # Thêm biểu diễn ký tự nếu có thể
        if input_format == 'char':
            try:
                response['ciphertext_char'] = binary_to_char(result['result'])
            except ValueError:
                response['ciphertext_char'] = None
        
        # Thêm thông tin từng bước nếu được yêu cầu
        if verbose:
            response['steps'] = result['steps']
            # Use the initial state captured inside algorithm (before any steps)
            response['initial_state'] = result.get('initial_state')
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': f'Mã hóa thất bại: {str(e)}'}), 500


@app.route('/api/decrypt', methods=['POST'])
def decrypt():
    """Giải mã ciphertext bằng TinyA5/1."""
    try:
        data = request.get_json()
        
        # Kiểm tra các trường bắt buộc
        if not data or 'ciphertext' not in data or 'key' not in data:
            return jsonify({'error': 'Thiếu các trường bắt buộc: ciphertext, key'}), 400
        
        ciphertext = data['ciphertext']
        key = data['key']
        input_format = data.get('input_format', 'binary')  # 'binary' or 'char'
        verbose = data.get('verbose', False)
        
        # Kiểm tra khóa
        valid_key, key_msg = validate_key(key)
        if not valid_key:
            return jsonify({'error': f'Kiểm tra khóa thất bại: {key_msg}'}), 400
        
        # Kiểm tra và chuyển đổi dữ liệu
        if input_format == 'char':
            valid_data, data_msg = validate_char_data(ciphertext)
            if not valid_data:
                return jsonify({'error': f'Kiểm tra dữ liệu thất bại: {data_msg}'}), 400
            try:
                binary_data = char_to_binary(ciphertext)
            except ValueError as e:
                return jsonify({'error': f'Chuyển đổi ký tự thất bại: {e}'}), 400
        else:
            valid_data, data_msg = validate_binary_data(ciphertext)
            if not valid_data:
                return jsonify({'error': f'Kiểm tra dữ liệu thất bại: {data_msg}'}), 400
            binary_data = ciphertext
        
        # Thực hiện giải mã (giống như mã hóa với stream cipher)
        cipher = TinyA51(key)
        result = cipher.encrypt_decrypt(binary_data, verbose=verbose)
        
        # Chuẩn bị phản hồi
        response = {
            'success': True,
            'ciphertext': ciphertext,
            'ciphertext_binary': binary_data,
            'plaintext': result['result'],
            'key': key,
            'input_format': input_format
        }
        
        # Thêm biểu diễn ký tự nếu có thể
        if input_format == 'char':
            try:
                response['plaintext_char'] = binary_to_char(result['result'])
            except ValueError:
                response['plaintext_char'] = None
        
        # Thêm thông tin từng bước nếu được yêu cầu
        if verbose:
            response['steps'] = result['steps']
            # Use the initial state captured inside algorithm (before any steps)
            response['initial_state'] = result.get('initial_state')
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': f'Giải mã thất bại: {str(e)}'}), 500


@app.route('/api/validate', methods=['POST'])
def validate():
    """Kiểm tra dữ liệu đầu vào mà không xử lý."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Không có dữ liệu được cung cấp'}), 400
        
        key = data.get('key', '')
        input_data = data.get('data', '')
        input_format = data.get('input_format', 'binary')
        
        result = {'valid': True, 'errors': []}
        
        # Kiểm tra khóa
        if key:
            valid_key, key_msg = validate_key(key)
            if not valid_key:
                result['valid'] = False
                result['errors'].append(f'Khóa: {key_msg}')
        
        # Kiểm tra dữ liệu
        if input_data:
            if input_format == 'char':
                valid_data, data_msg = validate_char_data(input_data)
                if not valid_data:
                    result['valid'] = False
                    result['errors'].append(f'Dữ liệu: {data_msg}')
            else:
                valid_data, data_msg = validate_binary_data(input_data)
                if not valid_data:
                    result['valid'] = False
                    result['errors'].append(f'Dữ liệu: {data_msg}')
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': f'Kiểm tra thất bại: {str(e)}'}), 500


@app.route('/api/convert', methods=['POST'])
def convert():
    """Chuyển đổi giữa định dạng nhị phân và ký tự."""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data or 'from_format' not in data:
            return jsonify({'error': 'Thiếu các trường bắt buộc: text, from_format'}), 400
        
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
                return jsonify({'error': f'Chuyển đổi ký tự sang nhị phân thất bại: {e}'}), 400
        
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
                return jsonify({'error': f'Chuyển đổi nhị phân sang ký tự thất bại: {e}'}), 400
        
        else:
            return jsonify({'error': 'Định dạng from_format không hợp lệ. Sử dụng "char" hoặc "binary"'}), 400
    
    except Exception as e:
        return jsonify({'error': f'Chuyển đổi thất bại: {str(e)}'}), 500


@app.errorhandler(404)
def not_found(error):
    """Xử lý lỗi 404."""
    return jsonify({'error': 'Không tìm thấy endpoint'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Xử lý lỗi 500."""
    return jsonify({'error': 'Lỗi máy chủ nội bộ'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    print("Đang khởi động TinyA5/1 Web Visualizer...")
    print(f"Mở trình duyệt và truy cập: http://0.0.0.0:{port}")
    print("Nhấn Ctrl+C để dừng máy chủ")
    app.run(debug=debug, host='0.0.0.0', port=port)
