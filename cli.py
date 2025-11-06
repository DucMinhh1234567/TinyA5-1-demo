import argparse
import sys
from tinya51 import TinyA51, char_to_binary, binary_to_char, validate_key, validate_binary_data, validate_char_data


def print_register_state(registers, label=""):
    """In trạng thái thanh ghi theo định dạng."""
    print(f"{label}X: {' '.join(map(str, registers['X']))}")
    print(f"{label}Y: {' '.join(map(str, registers['Y']))}")
    print(f"{label}Z: {' '.join(map(str, registers['Z']))}")


def print_step(step, step_num):
    """In thông tin chi tiết từng bước."""
    print(f"\n{'='*50}")
    print(f"BƯỚC {step_num}")
    print(f"{'='*50}")
    
    print(f"Bit điều khiển: x1={step['x1']}, y3={step['y3']}, z3={step['z3']}")
    print(f"Hàm đa số: maj({step['x1']}, {step['y3']}, {step['z3']}) = {step['majority']}")
    
    print(f"\nXoay thanh ghi:")
    print(f"  Xoay X: {step['rotate_X']}")
    print(f"  Xoay Y: {step['rotate_Y']}")
    print(f"  Xoay Z: {step['rotate_Z']}")
    
    print(f"\nTrạng thái thanh ghi:")
    print("  Trước khi xoay:")
    print_register_state({
        'X': step['X_before'],
        'Y': step['Y_before'],
        'Z': step['Z_before']
    }, "    ")
    
    print("  Sau khi xoay:")
    print_register_state({
        'X': step['X_after'],
        'Y': step['Y_after'],
        'Z': step['Z_after']
    }, "    ")
    
    print(f"\nTạo keystream:")
    print(f"  s = x5 XOR y7 XOR z8 = {step['X_after'][5]} XOR {step['Y_after'][7]} XOR {step['Z_after'][8]} = {step['keystream_bit']}")
    
    print(f"\nMã hóa:")
    print(f"  Bit dữ liệu: {step['data_bit']}")
    print(f"  Bit mã: {step['data_bit']} XOR {step['keystream_bit']} = {step['cipher_bit']}")


def interactive_mode():
    """Chế độ tương tác cho công cụ CLI."""
    print("Công Cụ Mã Hóa/Giải Mã TinyA5/1")
    print("="*40)
    
    while True:
        print("\nTùy chọn:")
        print("1. Mã hóa")
        print("2. Giải mã")
        print("3. Thoát")
        
        choice = input("\nChọn tùy chọn (1-3): ").strip()
        
        if choice == '3':
            print("Tạm biệt!")
            break
        elif choice not in ['1', '2']:
            print("Lựa chọn không hợp lệ. Vui lòng chọn 1, 2 hoặc 3.")
            continue
        
        # Get input format
        print("\nĐịnh dạng đầu vào:")
        print("1. Nhị phân (ví dụ: '111')")
        print("2. Ký tự (ví dụ: 'H' cho A-H)")
        
        format_choice = input("Chọn định dạng (1-2): ").strip()
        if format_choice not in ['1', '2']:
            print("Lựa chọn định dạng không hợp lệ.")
            continue
        
        # Get data
        if format_choice == '1':
            data = input("Nhập dữ liệu nhị phân: ").strip()
            is_binary = True
        else:
            data = input("Nhập ký tự (A-H): ").strip()
            is_binary = False
        
        # Get key
        key = input("Nhập khóa 23 bit: ").strip()
        
        # Validate inputs
        valid_key, key_msg = validate_key(key)
        if not valid_key:
            print(f"Lỗi khóa: {key_msg}")
            continue
        
        if is_binary:
            valid_data, data_msg = validate_binary_data(data)
        else:
            valid_data, data_msg = validate_char_data(data)
        
        if not valid_data:
            print(f"Lỗi dữ liệu: {data_msg}")
            continue
        
        # Convert data to binary if needed
        if not is_binary:
            try:
                binary_data = char_to_binary(data)
                print(f"Đã chuyển đổi sang nhị phân: {binary_data}")
            except ValueError as e:
                print(f"Lỗi chuyển đổi: {e}")
                continue
        else:
            binary_data = data
        
        # Get mode
        print("\nChế độ đầu ra:")
        print("1. Tức thì (chỉ hiển thị kết quả)")
        print("2. Chi tiết (hiển thị từng bước)")
        
        mode_choice = input("Chọn chế độ (1-2): ").strip()
        verbose = mode_choice == '2'
        
        # Process encryption/decryption
        try:
            cipher = TinyA51(key)
            
            if choice == '1':
                print(f"\nĐang mã hóa '{data}' với khóa '{key}'...")
                result = cipher.encrypt_decrypt(binary_data, verbose=verbose)
                
                if verbose:
                    print(f"\nTrạng thái thanh ghi ban đầu:")
                    if 'initial_state' in result:
                        print_register_state(result['initial_state'])
                    else:
                        print_register_state(cipher.get_register_state())
                    
                    for i, step in enumerate(result['steps']):
                        print_step(step, i)
                    
                    print(f"\n{'='*50}")
                    print("KẾT QUẢ CUỐI CÙNG")
                    print(f"{'='*50}")
                
                print(f"Plaintext: {data}")
                if not is_binary:
                    print(f"Plaintext (nhị phân): {binary_data}")
                print(f"Ciphertext (nhị phân): {result['result']}")
                if not is_binary:
                    try:
                        ciphertext_chars = binary_to_char(result['result'])
                        print(f"Ciphertext (ký tự): {ciphertext_chars}")
                    except ValueError:
                        print("Ciphertext không thể chuyển đổi sang ký tự (không phải bội số của 3)")
                
            else:  # Decrypt
                print(f"\nĐang giải mã '{data}' với khóa '{key}'...")
                result = cipher.encrypt_decrypt(binary_data, verbose=verbose)
                
                if verbose:
                    print(f"\nTrạng thái thanh ghi ban đầu:")
                    if 'initial_state' in result:
                        print_register_state(result['initial_state'])
                    else:
                        print_register_state(cipher.get_register_state())
                    
                    for i, step in enumerate(result['steps']):
                        print_step(step, i)
                    
                    print(f"\n{'='*50}")
                    print("KẾT QUẢ CUỐI CÙNG")
                    print(f"{'='*50}")
                
                print(f"Ciphertext: {data}")
                if not is_binary:
                    print(f"Ciphertext (nhị phân): {binary_data}")
                print(f"Plaintext (nhị phân): {result['result']}")
                if not is_binary:
                    try:
                        plaintext_chars = binary_to_char(result['result'])
                        print(f"Plaintext (ký tự): {plaintext_chars}")
                    except ValueError:
                        print("Plaintext không thể chuyển đổi sang ký tự (không phải bội số của 3)")
        
        except Exception as e:
            print(f"Lỗi: {e}")


def main():
    """Hàm CLI chính."""
    parser = argparse.ArgumentParser(
        description="Công Cụ Dòng Lệnh TinyA5/1 Stream Cipher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
  python cli.py --interactive
  python cli.py --encrypt --data "111" --key "10010101001110100110000"
  python cli.py --decrypt --data "011" --key "10010101001110100110000" --verbose
  python cli.py --encrypt --data "H" --key "10010101001110100110000" --char
        """
    )
    
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Chạy ở chế độ tương tác')
    
    parser.add_argument('--encrypt', '-e', action='store_true',
                       help='Mã hóa dữ liệu')
    parser.add_argument('--decrypt', '-d', action='store_true',
                       help='Giải mã dữ liệu')
    
    parser.add_argument('--data', type=str,
                       help='Dữ liệu để mã hóa/giải mã')
    parser.add_argument('--key', type=str,
                       help='Khóa nhị phân 23 bit')
    
    parser.add_argument('--char', action='store_true',
                       help='Dữ liệu đầu vào là ký tự (A-H) thay vì nhị phân')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Hiển thị thực thi từng bước')
    
    args = parser.parse_args()
    
    # Interactive mode
    if args.interactive:
        interactive_mode()
        return
    
    # Command line mode
    if not args.encrypt and not args.decrypt:
        print("Lỗi: Phải chỉ định --encrypt hoặc --decrypt")
        parser.print_help()
        sys.exit(1)
    
    if not args.data or not args.key:
        print("Lỗi: Phải chỉ định --data và --key")
        parser.print_help()
        sys.exit(1)
    
    # Validate key
    valid_key, key_msg = validate_key(args.key)
    if not valid_key:
        print(f"Lỗi khóa: {key_msg}")
        sys.exit(1)
    
    # Validate data
    if args.char:
        valid_data, data_msg = validate_char_data(args.data)
        if not valid_data:
            print(f"Lỗi dữ liệu: {data_msg}")
            sys.exit(1)
        try:
            binary_data = char_to_binary(args.data)
        except ValueError as e:
            print(f"Lỗi chuyển đổi: {e}")
            sys.exit(1)
    else:
        valid_data, data_msg = validate_binary_data(args.data)
        if not valid_data:
            print(f"Lỗi dữ liệu: {data_msg}")
            sys.exit(1)
        binary_data = args.data
    
    # Process encryption/decryption
    try:
        cipher = TinyA51(args.key)
        result = cipher.encrypt_decrypt(binary_data, verbose=args.verbose)
        
        if args.verbose:
            print(f"Trạng thái thanh ghi ban đầu:")
            if 'initial_state' in result:
                print_register_state(result['initial_state'])
            else:
                print_register_state(cipher.get_register_state())
            
            for i, step in enumerate(result['steps']):
                print_step(step, i)
            
            print(f"\n{'='*50}")
            print("KẾT QUẢ CUỐI CÙNG")
            print(f"{'='*50}")
        
        if args.encrypt:
            print(f"Plaintext: {args.data}")
            if args.char:
                print(f"Plaintext (nhị phân): {binary_data}")
            print(f"Ciphertext (nhị phân): {result['result']}")
            if args.char:
                try:
                    ciphertext_chars = binary_to_char(result['result'])
                    print(f"Ciphertext (ký tự): {ciphertext_chars}")
                except ValueError:
                    print("Ciphertext không thể chuyển đổi sang ký tự")
        else:  # Decrypt
            print(f"Ciphertext: {args.data}")
            if args.char:
                print(f"Ciphertext (nhị phân): {binary_data}")
            print(f"Plaintext (nhị phân): {result['result']}")
            if args.char:
                try:
                    plaintext_chars = binary_to_char(result['result'])
                    print(f"Plaintext (ký tự): {plaintext_chars}")
                except ValueError:
                    print("Plaintext không thể chuyển đổi sang ký tự")
    
    except Exception as e:
        print(f"Lỗi: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
