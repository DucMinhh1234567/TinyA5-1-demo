"""
TinyA5/1 Stream Cipher Implementation
Based on the algorithm described in the ATBMTT document.

This module implements the TinyA5/1 algorithm with:
- 3 registers: X (6 bits), Y (8 bits), Z (9 bits)
- 23-bit key
- Majority function for conditional register rotation
- Step-by-step execution tracking for visualization
"""

class TinyA51:
    def __init__(self, key):
        """
        Initialize TinyA5/1 with a 23-bit key.
        
        Args:
            key (str): 23-bit binary string
        """
        if len(key) != 23:
            raise ValueError("Key must be exactly 23 bits")
        if not all(c in '01' for c in key):
            raise ValueError("Key must contain only 0s and 1s")
        
        self.key = key
        self.reset()
    
    def reset(self):
        """Reset registers to initial state based on key."""
        # Split 23-bit key into registers
        # X: 6 bits, Y: 8 bits, Z: 9 bits
        self.X = list(self.key[:6])    # x0, x1, ..., x5
        self.Y = list(self.key[6:14])  # y0, y1, ..., y7
        self.Z = list(self.key[14:23]) # z0, z1, ..., z8
        
        # Convert to integers for easier manipulation
        self.X = [int(bit) for bit in self.X]
        self.Y = [int(bit) for bit in self.Y]
        self.Z = [int(bit) for bit in self.Z]
    
    def majority(self, x2, y7, z8):
        """
        Calculate majority function: maj(x2, y7, z8)
        Returns 1 if 2 or more bits are 1, otherwise 0.
        """
        return 1 if (x2 + y7 + z8) >= 2 else 0
    
    def rotate_X(self):
        """Rotate register X: t = x3 ⊕ x4 ⊕ x5, then shift right and set x0 = t"""
        t = self.X[3] ^ self.X[4] ^ self.X[5]
        # Shift right: x5 = x4, x4 = x3, ..., x1 = x0
        for i in range(5, 0, -1):
            self.X[i] = self.X[i-1]
        self.X[0] = t
    
    def rotate_Y(self):
        """Rotate register Y: t = y6 ⊕ y7, then shift right and set y0 = t"""
        t = self.Y[6] ^ self.Y[7]
        # Shift right: y7 = y6, y6 = y5, ..., y1 = y0
        for i in range(7, 0, -1):
            self.Y[i] = self.Y[i-1]
        self.Y[0] = t
    
    def rotate_Z(self):
        """
        Rotate register Z: t = z3 ⊕ z7 ⊕ z8, then shift right and set z0 = t
        Note: Based on the ATBMTT document, the feedback taps are z3, z7, z8
        """
        t = self.Z[3] ^ self.Z[7] ^ self.Z[8]
        # Shift right: z8 = z7, z7 = z6, ..., z1 = z0
        for i in range(8, 0, -1):
            self.Z[i] = self.Z[i-1]
        self.Z[0] = t
    
    def generate_bit(self, step_info=None):
        """
        Generate one bit of keystream.
        
        Args:
            step_info (dict): Optional dict to store step information for visualization
            
        Returns:
            int: Generated keystream bit
        """
        # Get control bits
        x2, y7, z8 = self.X[2], self.Y[7], self.Z[8]
        
        # Calculate majority
        m = self.majority(x2, y7, z8)
        
        # Determine which registers to rotate
        rotate_X = (x2 == m)
        rotate_Y = (y7 == m)
        rotate_Z = (z8 == m)
        
        # Store step information if requested
        if step_info is not None:
            step_info.update({
                'x2': x2, 'y7': y7, 'z8': z8,
                'majority': m,
                'rotate_X': rotate_X,
                'rotate_Y': rotate_Y,
                'rotate_Z': rotate_Z,
                'X_before': self.X.copy(),
                'Y_before': self.Y.copy(),
                'Z_before': self.Z.copy()
            })
        
        # Rotate registers based on majority function
        if rotate_X:
            self.rotate_X()
        if rotate_Y:
            self.rotate_Y()
        if rotate_Z:
            self.rotate_Z()
        
        # Generate keystream bit: s = x5 ⊕ y7 ⊕ z8
        s = self.X[5] ^ self.Y[7] ^ self.Z[8]
        
        # Store final state if requested
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
        Encrypt or decrypt data using TinyA5/1.
        
        Args:
            data (str): Binary string to encrypt/decrypt
            verbose (bool): If True, return step-by-step information
            
        Returns:
            dict: Result with ciphertext/plaintext and optional step details
        """
        if not all(c in '01' for c in data):
            raise ValueError("Data must contain only 0s and 1s")
        
        self.reset()
        result = []
        steps = []
        
        for i, bit in enumerate(data):
            step_info = {} if verbose else None
            keystream_bit = self.generate_bit(step_info)
            
            # XOR with data bit
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
        
        return result_dict
    
    def get_register_state(self):
        """Get current state of all registers."""
        return {
            'X': self.X.copy(),
            'Y': self.Y.copy(),
            'Z': self.Z.copy()
        }


def char_to_binary(text):
    """
    Convert characters A-H to 3-bit binary representation.
    
    Args:
        text (str): String containing characters A-H
        
    Returns:
        str: Binary representation
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
            raise ValueError(f"Character '{char}' not supported. Use A-H only.")
    
    return ''.join(result)


def binary_to_char(binary):
    """
    Convert 3-bit binary strings to characters A-H.
    
    Args:
        binary (str): Binary string (length must be multiple of 3)
        
    Returns:
        str: Character representation
    """
    if len(binary) % 3 != 0:
        raise ValueError("Binary string length must be multiple of 3")
    
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
            raise ValueError(f"Invalid binary chunk '{chunk}'")
    
    return ''.join(result)


def validate_key(key):
    """Validate that key is a 23-bit binary string."""
    if len(key) != 23:
        return False, f"Key must be exactly 23 bits, got {len(key)}"
    if not all(c in '01' for c in key):
        return False, "Key must contain only 0s and 1s"
    return True, "Valid key"


def validate_binary_data(data):
    """Validate that data is a binary string."""
    if not all(c in '01' for c in data):
        return False, "Data must contain only 0s and 1s"
    return True, "Valid binary data"


def validate_char_data(data):
    """Validate that data contains only A-H characters."""
    if not all(c.upper() in 'ABCDEFGH' for c in data):
        return False, "Data must contain only characters A-H"
    return True, "Valid character data"


if __name__ == "__main__":
    # Example usage
    key = "10010101001110100110000"  # 23-bit key
    plaintext = "111"  # Binary representation of 'H'
    
    cipher = TinyA51(key)
    result = cipher.encrypt_decrypt(plaintext, verbose=True)
    
    print(f"Plaintext: {plaintext}")
    print(f"Key: {key}")
    print(f"Ciphertext: {result['result']}")
    print("\nStep-by-step execution:")
    
    for step in result['steps']:
        print(f"\nStep {step['step']}:")
        print(f"  Control bits: x2={step['x2']}, y7={step['y7']}, z8={step['z8']}")
        print(f"  Majority: {step['majority']}")
        print(f"  Rotate: X={step['rotate_X']}, Y={step['rotate_Y']}, Z={step['rotate_Z']}")
        print(f"  X: {step['X_before']} -> {step['X_after']}")
        print(f"  Y: {step['Y_before']} -> {step['Y_after']}")
        print(f"  Z: {step['Z_before']} -> {step['Z_after']}")
        print(f"  Keystream bit: {step['keystream_bit']}")
        print(f"  Data bit: {step['data_bit']}, Cipher bit: {step['cipher_bit']}")
