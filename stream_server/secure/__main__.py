from getpass import getpass
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from pki_helpers import (
    generate_private_key,
    generate_public_key,
    sign_csr,
    generate_csr
)


# Details
country = 'ZA'
state = 'Western Province'
locality = 'Cape Town'
org = 'Lynk Solutions, Watchdog'
hostname = '10.0.0.118'

# CA
ca_public_key_path = "ssl/ca.crt"
ca_private_key_path = "ssl/ca.key"
ca_secret_pass_path = "secret"

# Server
server_public_key_path = "ssl/cert.crt"
server_private_key_path = "ssl/cert.key"
server_csr_path = "ssl/cert.csr"
server_secret_pass_path = "secret"

# Store Password
passwords = open("ssl/ssl_passwords.txt", "w")
passwords.write(server_secret_pass_path)
passwords.close()

# Generate CA Private Key
private_key = generate_private_key(
    ca_private_key_path,
    ca_secret_pass_path
)

# Generate CA Public Key
generate_public_key(
    private_key,
    filename=ca_public_key_path,
    country=country,
    state=state,
    locality=locality,
    org=org,
    hostname=hostname
)

# Generate Server Private Key
server_private_key = generate_private_key(
    server_private_key_path,
    server_secret_pass_path
)

# Generate Server Public Key .csr
generate_csr(
    server_private_key,
    filename=server_csr_path,
    country=country,
    state=state,
    locality=locality,
    org=org,
    alt_names=["localhost"],
    hostname=hostname
)

csr_file = open(server_csr_path, "rb")
csr = x509.load_pem_x509_csr(csr_file.read(), default_backend())

ca_public_key_file = open(ca_public_key_path, "rb")
ca_public_key = x509.load_pem_x509_certificate(
    ca_public_key_file.read(),
    default_backend()
)

ca_private_key_file = open(ca_private_key_path, "rb")
ca_private_key = serialization.load_pem_private_key(
    ca_private_key_file.read(),
    getpass().encode("utf-8"),
    default_backend(),
)

# Sign Server .csr Public Key with CA and Generate .crt Public Key
sign_csr(
    csr,
    ca_public_key,
    ca_private_key,
    server_public_key_path
)
