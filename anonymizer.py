import os
import sys
import pandas as pd
import hashlib
import argparse
from cryptography.fernet import Fernet
from typing import Dict
import logging
import hmac

logging.basicConfig(level=logging.INFO)


class DataAnonymizer:

    def __init__(self, secret_key_path: str):
        self.secret_key_path = secret_key_path
        self.secret_key = self.load_secret_key()

    def generate_secret_key(self):
        secret_key = Fernet.generate_key()
        with open(self.secret_key_path, 'wb') as key_file:
            key_file.write(secret_key)
        return secret_key

    def load_secret_key(self):
        if os.path.exists(self.secret_key_path):
            with open(self.secret_key_path, 'rb') as key_file:
                return key_file.read()
        else:
            logging.info('Secret key file does not exist. Generating a new secret key...')
            return self.generate_secret_key()

    def generate_pseudonyms(self, data: pd.Series, salt: str) -> Dict[str, str]:
        unique_entries = data.unique()
        pseudonyms = {}
        for entry in unique_entries:
            pseudonym = hashlib.sha256((salt + str(entry)).encode()).hexdigest()
            pseudonyms[entry] = pseudonym
        return pseudonyms

    def encrypt_pseudonym_mapping(self, pseudonym_mapping: Dict[str, str]) -> bytes:
        f = Fernet(self.secret_key)
        plaintext_mapping = '\n'.join([f'{k}:{v}' for k, v in pseudonym_mapping.items()])
        encrypted_mapping = f.encrypt(plaintext_mapping.encode())
        
        hmac_gen = hmac.new(self.secret_key, encrypted_mapping, 'sha256')
        hmac_value = hmac_gen.digest()

        return encrypted_mapping + hmac_value

    def decrypt_pseudonym_mapping(self, encrypted_mapping: bytes) -> Dict[str, str]:
        stored_hmac = encrypted_mapping[-32:]
        encrypted_data = encrypted_mapping[:-32]

        hmac_gen = hmac.new(self.secret_key, encrypted_data, 'sha256')
        computed_hmac = hmac_gen.digest()

        if hmac.compare_digest(stored_hmac, computed_hmac):
            f = Fernet(self.secret_key)
            decrypted_mapping = f.decrypt(encrypted_data).decode()
            pseudonym_mapping = dict(line.split(':') for line in decrypted_mapping.split('\n'))
            return pseudonym_mapping
        else:
            logging.error('Data integrity check failed. Encrypted mapping might have been tampered with.')
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Anonymize or revert dataset.')
    parser.add_argument('file_path', help='Path to the data file')
    parser.add_argument('operation', choices=['anonymize', 'revert'], help='Operation to perform')
    parser.add_argument('--cols', nargs='*', help='Specific columns to anonymize or revert', default=[])
    parser.add_argument('--key_path', help='Path to the secret key file', required=True)
    args = parser.parse_args()

    data_anonymizer = DataAnonymizer(secret_key_path=args.key_path)

    if args.operation == 'revert' and not os.path.exists(args.key_path):
        logging.error('Secret key file does not exist. Cannot revert data without the original secret key.')
        sys.exit(1)

    salt = os.urandom(16)
    
    try:
        data = pd.read_csv(args.file_path)
    except pd.errors.EmptyDataError as e:
        logging.error('The data file is empty. Error: %s', e)
        sys.exit(1)
    except pd.errors.ParserError as e:
        logging.error('Failed to parse the data file. Error: %s', e)
        sys.exit(1)

    pii_columns = args.cols if args.cols else data.columns

    if args.operation == 'anonymize':
        for col in pii_columns:
            pseudonym_mapping = data_anonymizer.generate_pseudonyms(data[col], salt.hex())
            data[col] = data[col].map(pseudonym_mapping)

            encrypted_mappings_file_path = os.path.join(os.path.dirname(args.file_path), f'pseudonym_key_{col}.enc')
            with open(encrypted_mappings_file_path, 'wb') as enc_file:
                enc_file.write(data_anonymizer.encrypt_pseudonym_mapping(pseudonym_mapping))

        data.to_csv(args.file_path, index=False)
        logging.info('Data anonymized successfully.')

    elif args.operation == 'revert':
        for col in pii_columns:
            encrypted_mappings_file_path = os.path.join(os.path.dirname(args.file_path), f'pseudonym_key_{col}.enc')
            if os.path.exists(encrypted_mappings_file_path):
                with open(encrypted_mappings_file_path, 'rb') as enc_file:
                    encrypted_mapping = enc_file.read()
                pseudonym_mapping = data_anonymizer.decrypt_pseudonym_mapping(encrypted_mapping)
                original_mapping = {v: k for k, v in pseudonym_mapping.items()}
                data[col] = data[col].map(original_mapping).fillna(data[col])

        data.to_csv(args.file_path, index=False)
        logging.info('Data reverted to original successfully.')


if __name__ == '__main__':
    main()
