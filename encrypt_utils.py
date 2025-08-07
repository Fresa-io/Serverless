#!/usr/bin/env python3
"""
Simple credential encryption/decryption utility
"""

import base64
import sys

def create_hash(access_key: str, secret_key: str, region: str) -> str:
    """Create a simple base64 hash for sharing"""
    creds_string = f"{access_key}:{secret_key}:{region}"
    return base64.b64encode(creds_string.encode()).decode()

def decode_hash(hashed_string: str) -> tuple:
    """Decode a simple base64 hash"""
    try:
        decoded = base64.b64decode(hashed_string.encode()).decode()
        access_key, secret_key, region = decoded.split(':', 2)
        return access_key, secret_key, region
    except Exception as e:
        raise ValueError(f"Failed to decode hash: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 encrypt_utils.py hash <access_key> <secret_key> <region>")
        print("  python3 encrypt_utils.py decrypt <encrypted_string>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "hash":
        if len(sys.argv) != 5:
            print("Error: hash command requires 3 arguments")
            sys.exit(1)
        
        access_key = sys.argv[2]
        secret_key = sys.argv[3]
        region = sys.argv[4]
        
        hashed = create_hash(access_key, secret_key, region)
        print(f"Hash: {hashed}")
        
    elif command == "decrypt":
        if len(sys.argv) != 3:
            print("Error: decrypt command requires 1 argument")
            sys.exit(1)
        
        encrypted_string = sys.argv[2]
        
        try:
            access_key, secret_key, region = decode_hash(encrypted_string)
            print(f"Access Key: {access_key}")
            print(f"Secret Key: {secret_key}")
            print(f"Region: {region}")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
            
    else:
        print(f"Unknown command: {command}")
        sys.exit(1) 