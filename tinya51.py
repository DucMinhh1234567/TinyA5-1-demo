"""
Triển khai mã dòng TinyA5/1


Mô-đun này hiện thực thuật toán TinyA5/1 với:
- 3 thanh ghi: X (6 bit), Y (8 bit), Z (9 bit)
- Khóa 23 bit
- Hàm đa số để xoay thanh ghi có điều kiện
- Theo dõi thực thi từng bước để trực quan hóa
"""

class TinyA51:
    def __init__(self, key):
        """
        Khởi tạo TinyA5/1 với khóa 23 bit.
        
        Args:
            key (str): Chuỗi nhị phân 23 bit
        """
        if len(key) != 23:
            raise ValueError("Khóa phải dài chính xác 23 bit")
        if not all(c in '01' for c in key):
            raise ValueError("Khóa chỉ được chứa các ký tự 0 và 1")
        
        self.key = key
        self.reset()
    
    def reset(self):
        """Đặt lại các thanh ghi về trạng thái ban đầu dựa trên khóa."""
        # Chia khóa 23 bit vào các thanh ghi
        # X: 6 bit, Y: 8 bit, Z: 9 bit
        self.X = list(self.key[:6])    # x0, x1, ..., x5
        self.Y = list(self.key[6:14])  # y0, y1, ..., y7
        self.Z = list(self.key[14:23]) # z0, z1, ..., z8
        
        # Chuyển thành số nguyên để thao tác dễ hơn
        self.X = [int(bit) for bit in self.X]
        self.Y = [int(bit) for bit in self.Y]
        self.Z = [int(bit) for bit in self.Z]
    
    def majority(self, x1, y3, z3):
        """
        Tính hàm đa số: maj(x1, y3, z3)
        Trả về 1 nếu có ít nhất 2 bit bằng 1, ngược lại trả về 0.
        Lưu ý: Ký hiệu dùng chỉ số bắt đầu từ 1 (x1, y3, z3) nhưng mảng trong mã dùng chỉ số bắt đầu từ 0 (x[1], y[3], z[3])
        """
        return 1 if (x1 + y3 + z3) >= 2 else 0
    
    def rotate_X(self):
        """Xoay thanh ghi X: t = x2 ⊕ x4 ⊕ x5 (chỉ số theo 1: 2,4,5; theo 0: 2,4,5), sau đó dịch phải và đặt x0 = t"""
        # Theo chỉ số bắt đầu từ 1: x2, x4, x5 = theo 0: 2, 4, 5
        t = self.X[2] ^ self.X[4] ^ self.X[5]
        # Dịch phải: x5 = x4, x4 = x3, ..., x1 = x0
        for i in range(5, 0, -1):
            self.X[i] = self.X[i-1]
        self.X[0] = t
    
    def rotate_Y(self):
        """Xoay thanh ghi Y: t = y6 ⊕ y7, sau đó dịch phải và đặt y0 = t"""
        t = self.Y[6] ^ self.Y[7]
        # Dịch phải: y7 = y6, y6 = y5, ..., y1 = y0
        for i in range(7, 0, -1):
            self.Y[i] = self.Y[i-1]
        self.Y[0] = t
    
    def rotate_Z(self):
        """
        Xoay thanh ghi Z: t = z2 ⊕ z7 ⊕ z8 (chỉ số theo 1: 2,7,8; theo 0: 2,7,8), sau đó dịch phải và đặt z0 = t
        Lưu ý: Theo tài liệu ATBMTT, các điểm hồi tiếp là z2, z7, z8
        """
        # Theo chỉ số bắt đầu từ 1: z2, z7, z8 = theo 0: 2, 7, 8
        t = self.Z[2] ^ self.Z[7] ^ self.Z[8]
        # Dịch phải: z8 = z7, z7 = z6, ..., z1 = z0
        for i in range(8, 0, -1):
            self.Z[i] = self.Z[i-1]
        self.Z[0] = t
    
    def generate_bit(self, step_info=None):
        """
        Sinh ra một bit của keystream.
        
        Args:
            step_info (dict): Từ điển tùy chọn để lưu thông tin từng bước nhằm trực quan hóa
            
        Returns:
            int: Bit keystream được sinh ra
        """
        # Lấy các bit điều khiển (chỉ số theo 1: x1, y3, z3 = theo 0: x[1], y[3], z[3])
        # Lưu ý: Trong tài liệu, ký hiệu dùng chỉ số bắt đầu từ 1, còn ở đây dùng mảng bắt đầu từ 0
        x1, y3, z3 = self.X[1], self.Y[3], self.Z[3]
        
        # Tính hàm đa số
        m = self.majority(x1, y3, z3)
        
        # Xác định các thanh ghi cần xoay
        rotate_X = (x1 == m)
        rotate_Y = (y3 == m)
        rotate_Z = (z3 == m)
        
        # Lưu thông tin bước nếu được yêu cầu
        if step_info is not None:
            step_info.update({
                'x1': x1, 'y3': y3, 'z3': z3,
                'majority': m,
                'rotate_X': rotate_X,
                'rotate_Y': rotate_Y,
                'rotate_Z': rotate_Z,
                'X_before': self.X.copy(),
                'Y_before': self.Y.copy(),
                'Z_before': self.Z.copy()
            })
        
        # Xoay các thanh ghi dựa vào hàm đa số
        if rotate_X:
            self.rotate_X()
        if rotate_Y:
            self.rotate_Y()
        if rotate_Z:
            self.rotate_Z()
        
        # Sinh bit keystream SAU khi xoay: s = x5 ⊕ y7 ⊕ z8 (chỉ số theo 1) = x[5] ⊕ y[7] ⊕ z[8] (theo 0)
        # Đây là các bit cuối của mỗi thanh ghi sau khi xoay
        s = self.X[5] ^ self.Y[7] ^ self.Z[8]
        
        # Lưu trạng thái cuối nếu được yêu cầu
        if step_info is not None:
            step_info.update({
                'X_after': self.X.copy(),
                'Y_after': self.Y.copy(),
                'Z_after': self.Z.copy(),
                'keystream_bit': s
            })
        
        return s
    
    def encrypt_decrypt(self, data, verbose=False):
        """
        Mã hóa hoặc giải mã dữ liệu bằng TinyA5/1.
        
        Args:
            data (str): Chuỗi nhị phân cần mã hóa/giải mã
            verbose (bool): Nếu True, trả về thông tin chi tiết từng bước
            
        Returns:
            dict: Kết quả gồm bản mã/bản rõ và chi tiết bước (tùy chọn)
        """
        if not all(c in '01' for c in data):
            raise ValueError("Dữ liệu chỉ được chứa các ký tự 0 và 1")
        
        self.reset()
        
        # Ghi lại trạng thái ban đầu cho chế độ chi tiết
        initial_state = None
        if verbose:
            initial_state = {
                'X': self.X.copy(),
                'Y': self.Y.copy(),
                'Z': self.Z.copy()
            }
        
        result = []
        steps = []
        
        for i, bit in enumerate(data):
            step_info = {} if verbose else None
            keystream_bit = self.generate_bit(step_info)
            
            # XOR với bit dữ liệu
            cipher_bit = int(bit) ^ keystream_bit
            result.append(str(cipher_bit))
            
            if verbose:
                step_info['data_bit'] = int(bit)
                step_info['cipher_bit'] = cipher_bit
                step_info['step'] = i
                steps.append(step_info)
        
        result_dict = {
            'result': ''.join(result),
            'input': data,
            'key': self.key
        }
        
        if verbose:
            result_dict['steps'] = steps
            result_dict['initial_state'] = initial_state
        
        return result_dict
    
    def get_register_state(self):
        """Lấy trạng thái hiện tại của tất cả các thanh ghi."""
        return {
            'X': self.X.copy(),
            'Y': self.Y.copy(),
            'Z': self.Z.copy()
        }


def char_to_binary(text):
    """
    Chuyển đổi các ký tự A-H thành biểu diễn nhị phân 3 bit.
    
    Args:
        text (str): Chuỗi chứa các ký tự A-H
        
    Returns:
        str: Biểu diễn nhị phân
    """
    char_map = {
        'A': '000', 'B': '001', 'C': '010', 'D': '011',
        'E': '100', 'F': '101', 'G': '110', 'H': '111'
    }
    
    result = []
    for char in text.upper():
        if char in char_map:
            result.append(char_map[char])
        else:
            raise ValueError(f"Ký tự '{char}' không được hỗ trợ. Chỉ dùng A-H.")
    
    return ''.join(result)


def binary_to_char(binary):
    """
    Chuyển đổi chuỗi nhị phân 3 bit thành các ký tự A-H.
    
    Args:
        binary (str): Chuỗi nhị phân (độ dài phải là bội số của 3)
        
    Returns:
        str: Biểu diễn ký tự
    """
    if len(binary) % 3 != 0:
        raise ValueError("Độ dài chuỗi nhị phân phải là bội số của 3")
    
    char_map = {
        '000': 'A', '001': 'B', '010': 'C', '011': 'D',
        '100': 'E', '101': 'F', '110': 'G', '111': 'H'
    }
    
    result = []
    for i in range(0, len(binary), 3):
        chunk = binary[i:i+3]
        if chunk in char_map:
            result.append(char_map[chunk])
        else:
            raise ValueError(f"Nhóm nhị phân không hợp lệ '{chunk}'")
    
    return ''.join(result)


def validate_key(key):
    """Kiểm tra khóa là chuỗi nhị phân 23 bit."""
    if len(key) != 23:
        return False, f"Khóa phải dài chính xác 23 bit, hiện là {len(key)}"
    if not all(c in '01' for c in key):
        return False, "Khóa chỉ được chứa các ký tự 0 và 1"
    return True, "Khóa hợp lệ"


def validate_binary_data(data):
    """Kiểm tra dữ liệu là chuỗi nhị phân."""
    if not all(c in '01' for c in data):
        return False, "Dữ liệu chỉ được chứa các ký tự 0 và 1"
    return True, "Dữ liệu nhị phân hợp lệ"


def validate_char_data(data):
    """Kiểm tra dữ liệu chỉ chứa các ký tự A-H."""
    if not all(c.upper() in 'ABCDEFGH' for c in data):
        return False, "Dữ liệu chỉ được chứa các ký tự A-H"
    return True, "Dữ liệu ký tự hợp lệ"


if __name__ == "__main__":
    # Ví dụ sử dụng
    key = "10010101001110100110000"  # Khóa 23 bit
    plaintext = "111"  # Biểu diễn nhị phân của 'H'
    
    cipher = TinyA51(key)
    result = cipher.encrypt_decrypt(plaintext, verbose=True)
    
    print(f"Bản rõ: {plaintext}")
    print(f"Khóa: {key}")
    print(f"Bản mã: {result['result']}")
    print("\nThực thi từng bước:")
    
    for step in result['steps']:
        print(f"\nBước {step['step']}:")
        print(f"  Bit điều khiển: x1={step['x1']}, y3={step['y3']}, z3={step['z3']}")
        print(f"  Đa số: {step['majority']}")
        print(f"  Xoay: X={step['rotate_X']}, Y={step['rotate_Y']}, Z={step['rotate_Z']}")
        print(f"  X: {step['X_before']} -> {step['X_after']}")
        print(f"  Y: {step['Y_before']} -> {step['Y_after']}")
        print(f"  Z: {step['Z_before']} -> {step['Z_after']}")
        print(f"  Bit keystream: {step['keystream_bit']}")
        print(f"  Bit dữ liệu: {step['data_bit']}, Bit mã: {step['cipher_bit']}")
