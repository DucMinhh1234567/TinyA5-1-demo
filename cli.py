#!/usr/bin/env python3
"""
TinyA5/1 CLI Tool
Command-line interface for TinyA5/1 encryption/decryption with immediate and verbose modes.
"""

import argparse
import sys
from tinya51 import TinyA51, char_to_binary, binary_to_char, validate_key, validate_binary_data, validate_char_data


def print_register_state(registers, label=""):
    """Print register state in a formatted way."""
    print(f"{label}X: {' '.join(map(str, registers['X']))}")
    print(f"{label}Y: {' '.join(map(str, registers['Y']))}")
    print(f"{label}Z: {' '.join(map(str, registers['Z']))}")


def print_step(step, step_num):
    """Print detailed step information."""
    print(f"\n{'='*50}")
    print(f"STEP {step_num}")
    print(f"{'='*50}")
    
    print(f"Control bits: x2={step['x2']}, y7={step['y7']}, z8={step['z8']}")
    print(f"Majority function: maj({step['x2']}, {step['y7']}, {step['z8']}) = {step['majority']}")
    
    print(f"\nRegister rotations:")
    print(f"  Rotate X: {step['rotate_X']}")
    print(f"  Rotate Y: {step['rotate_Y']}")
    print(f"  Rotate Z: {step['rotate_Z']}")
    
    print(f"\nRegister states:")
    print("  Before rotation:")
    print_register_state({
        'X': step['X_before'],
        'Y': step['Y_before'],
        'Z': step['Z_before']
    }, "    ")
    
    print("  After rotation:")
    print_register_state({
        'X': step['X_after'],
        'Y': step['Y_after'],
        'Z': step['Z_after']
    }, "    ")
    
    print(f"\nKeystream generation:")
    print(f"  s = x5 ⊕ y7 ⊕ z8 = {step['X_after'][5]} ⊕ {step['Y_after'][7]} ⊕ {step['Z_after'][8]} = {step['keystream_bit']}")
    
    print(f"\nEncryption:")
    print(f"  Data bit: {step['data_bit']}")
    print(f"  Cipher bit: {step['data_bit']} ⊕ {step['keystream_bit']} = {step['cipher_bit']}")


def interactive_mode():
    """Interactive mode for CLI tool."""
    print("TinyA5/1 Encryption/Decryption Tool")
    print("="*40)
    
    while True:
        print("\nOptions:")
        print("1. Encrypt")
        print("2. Decrypt")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '3':
            print("Goodbye!")
            break
        elif choice not in ['1', '2']:
            print("Invalid choice. Please select 1, 2, or 3.")
            continue
        
        # Get input format
        print("\nInput format:")
        print("1. Binary (e.g., '111')")
        print("2. Characters (e.g., 'H' for A-H)")
        
        format_choice = input("Select format (1-2): ").strip()
        if format_choice not in ['1', '2']:
            print("Invalid format choice.")
            continue
        
        # Get data
        if format_choice == '1':
            data = input("Enter binary data: ").strip()
            is_binary = True
        else:
            data = input("Enter characters (A-H): ").strip()
            is_binary = False
        
        # Get key
        key = input("Enter 23-bit key: ").strip()
        
        # Validate inputs
        valid_key, key_msg = validate_key(key)
        if not valid_key:
            print(f"Key error: {key_msg}")
            continue
        
        if is_binary:
            valid_data, data_msg = validate_binary_data(data)
        else:
            valid_data, data_msg = validate_char_data(data)
        
        if not valid_data:
            print(f"Data error: {data_msg}")
            continue
        
        # Convert data to binary if needed
        if not is_binary:
            try:
                binary_data = char_to_binary(data)
                print(f"Converted to binary: {binary_data}")
            except ValueError as e:
                print(f"Conversion error: {e}")
                continue
        else:
            binary_data = data
        
        # Get mode
        print("\nOutput mode:")
        print("1. Immediate (show result only)")
        print("2. Verbose (show step-by-step)")
        
        mode_choice = input("Select mode (1-2): ").strip()
        verbose = mode_choice == '2'
        
        # Process encryption/decryption
        try:
            cipher = TinyA51(key)
            
            if choice == '1':
                print(f"\nEncrypting '{data}' with key '{key}'...")
                result = cipher.encrypt_decrypt(binary_data, verbose=verbose)
                
                if verbose:
                    print(f"\nInitial register state:")
                    print_register_state(cipher.get_register_state())
                    
                    for i, step in enumerate(result['steps']):
                        print_step(step, i)
                    
                    print(f"\n{'='*50}")
                    print("FINAL RESULT")
                    print(f"{'='*50}")
                
                print(f"Plaintext: {data}")
                if not is_binary:
                    print(f"Plaintext (binary): {binary_data}")
                print(f"Ciphertext (binary): {result['result']}")
                if not is_binary:
                    try:
                        ciphertext_chars = binary_to_char(result['result'])
                        print(f"Ciphertext (characters): {ciphertext_chars}")
                    except ValueError:
                        print("Ciphertext cannot be converted to characters (not multiple of 3)")
                
            else:  # Decrypt
                print(f"\nDecrypting '{data}' with key '{key}'...")
                result = cipher.encrypt_decrypt(binary_data, verbose=verbose)
                
                if verbose:
                    print(f"\nInitial register state:")
                    print_register_state(cipher.get_register_state())
                    
                    for i, step in enumerate(result['steps']):
                        print_step(step, i)
                    
                    print(f"\n{'='*50}")
                    print("FINAL RESULT")
                    print(f"{'='*50}")
                
                print(f"Ciphertext: {data}")
                if not is_binary:
                    print(f"Ciphertext (binary): {binary_data}")
                print(f"Plaintext (binary): {result['result']}")
                if not is_binary:
                    try:
                        plaintext_chars = binary_to_char(result['result'])
                        print(f"Plaintext (characters): {plaintext_chars}")
                    except ValueError:
                        print("Plaintext cannot be converted to characters (not multiple of 3)")
        
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="TinyA5/1 Stream Cipher CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py --interactive
  python cli.py --encrypt --data "111" --key "10010101001110100110000"
  python cli.py --decrypt --data "011" --key "10010101001110100110000" --verbose
  python cli.py --encrypt --data "H" --key "10010101001110100110000" --char
        """
    )
    
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run in interactive mode')
    
    parser.add_argument('--encrypt', '-e', action='store_true',
                       help='Encrypt data')
    parser.add_argument('--decrypt', '-d', action='store_true',
                       help='Decrypt data')
    
    parser.add_argument('--data', type=str,
                       help='Data to encrypt/decrypt')
    parser.add_argument('--key', type=str,
                       help='23-bit binary key')
    
    parser.add_argument('--char', action='store_true',
                       help='Input data is characters (A-H) instead of binary')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show step-by-step execution')
    
    args = parser.parse_args()
    
    # Interactive mode
    if args.interactive:
        interactive_mode()
        return
    
    # Command line mode
    if not args.encrypt and not args.decrypt:
        print("Error: Must specify --encrypt or --decrypt")
        parser.print_help()
        sys.exit(1)
    
    if not args.data or not args.key:
        print("Error: Must specify --data and --key")
        parser.print_help()
        sys.exit(1)
    
    # Validate key
    valid_key, key_msg = validate_key(args.key)
    if not valid_key:
        print(f"Key error: {key_msg}")
        sys.exit(1)
    
    # Validate data
    if args.char:
        valid_data, data_msg = validate_char_data(args.data)
        if not valid_data:
            print(f"Data error: {data_msg}")
            sys.exit(1)
        try:
            binary_data = char_to_binary(args.data)
        except ValueError as e:
            print(f"Conversion error: {e}")
            sys.exit(1)
    else:
        valid_data, data_msg = validate_binary_data(args.data)
        if not valid_data:
            print(f"Data error: {data_msg}")
            sys.exit(1)
        binary_data = args.data
    
    # Process encryption/decryption
    try:
        cipher = TinyA51(args.key)
        result = cipher.encrypt_decrypt(binary_data, verbose=args.verbose)
        
        if args.verbose:
            print(f"Initial register state:")
            print_register_state(cipher.get_register_state())
            
            for i, step in enumerate(result['steps']):
                print_step(step, i)
            
            print(f"\n{'='*50}")
            print("FINAL RESULT")
            print(f"{'='*50}")
        
        if args.encrypt:
            print(f"Plaintext: {args.data}")
            if args.char:
                print(f"Plaintext (binary): {binary_data}")
            print(f"Ciphertext (binary): {result['result']}")
            if args.char:
                try:
                    ciphertext_chars = binary_to_char(result['result'])
                    print(f"Ciphertext (characters): {ciphertext_chars}")
                except ValueError:
                    print("Ciphertext cannot be converted to characters")
        else:  # Decrypt
            print(f"Ciphertext: {args.data}")
            if args.char:
                print(f"Ciphertext (binary): {binary_data}")
            print(f"Plaintext (binary): {result['result']}")
            if args.char:
                try:
                    plaintext_chars = binary_to_char(result['result'])
                    print(f"Plaintext (characters): {plaintext_chars}")
                except ValueError:
                    print("Plaintext cannot be converted to characters")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
