import json
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.backends import default_backend
import time 

# Header数据
header = {
    "alg": "EdDSA",
    "kid": "K7H25ADDF6"
}

# Payload数据
payload = {
    "sub": "2GDYBB5C7G",
    "iat": int(time.time()) - 30,
    "exp": int(time.time()) + 900
}

# 将字典转换为JSON字符串
header_json = json.dumps(header, separators=(',', ':'))
payload_json = json.dumps(payload, separators=(',', ':'))

# Base64URL编码
header_base64 = base64.urlsafe_b64encode(header_json.encode()).decode().rstrip('=')
payload_base64 = base64.urlsafe_b64encode(payload_json.encode()).decode().rstrip('=')

# 拼接结果
jwt_part = f"{header_base64}.{payload_base64}"

print("Header JSON:", header_json)
print("Payload JSON:", payload_json)
print("Header Base64URL:", header_base64)
print("Payload Base64URL:", payload_base64)
print("拼接结果:", jwt_part)

# 私钥
private_key_pem = """-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIALf66UMY4i5qMg7R8AKbkil+0HEYxIoiezagC8T4UN+
-----END PRIVATE KEY-----"""

# 加载私钥
private_key = serialization.load_pem_private_key(
    private_key_pem.encode(),
    password=None,
    backend=default_backend()
)

# 使用Ed25519算法签名
signature = private_key.sign(jwt_part.encode())

# 对签名结果进行Base64URL编码
signature_base64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')

print("\n签名结果 (十六进制):", signature.hex())
print("签名结果 Base64URL:", signature_base64)

# 完整的JWT
jwt_complete = f"{jwt_part}.{signature_base64}"
print("完整JWT:", jwt_complete)