import datetime
import hashlib
import os

def _xor_string(input_string: str):
    xor_key = os.getenv('XOR_KEY')
    if not xor_key:
        raise NoEnvValue("XOR_KEY")
    input_bytes = input_string.encode()
    key_bytes = xor_key.encode()
    
    xored_bytes = bytearray()
    for i in range(len(input_bytes)):
        xored_bytes.append(input_bytes[i] ^ key_bytes[i % len(key_bytes)])
    
    return bytes(xored_bytes)

def hash_str(input_string):
    #Extra step before hashing to randomise even more the EI
    #This is done BEFORE the hashing, so even who has the "xor_key" CANNOT reverse the EIDs 
    xored_result = _xor_string(input_string)
    
    sha256 = hashlib.sha256()
    sha256.update(xored_result)
    
    return sha256.hexdigest()

def now_utc() -> datetime:
    return datetime.datetime.now(datetime.timezone.utc)