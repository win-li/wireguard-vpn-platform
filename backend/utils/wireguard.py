import secrets
import string
from typing import Dict, Tuple

def generate_wireguard_keys() -> Tuple[str, str]:
    """
    Generate WireGuard private and public keys (mock implementation)
    Returns tuple of (private_key, public_key)
    Note: In a real implementation, we would use wg command-line tools
    For now, we generate random keys for demonstration purposes
    """
    # In a real implementation, we would use:
    # private_key = subprocess.run(["wg", "genkey"], capture_output=True, text=True).stdout.strip()
    # public_key = subprocess.run(["wg", "pubkey"], input=private_key, capture_output=True, text=True).stdout.strip()

    # For demo purposes, generating random keys
    private_key = "".join(secrets.choice(string.ascii_letters + string.digits + "+/=") for _ in range(44))
    # Simplified public key generation (in reality this would be derived from private key)
    public_key = "".join(secrets.choice(string.ascii_letters + string.digits + "+/=") for _ in range(44))

    return private_key, public_key

def generate_client_config(server_public_key: str, client_private_key: str,
                          server_endpoint: str, client_ip: str,
                          dns_server: str = "8.8.8.8") -> str:
    """
    Generate client-side WireGuard configuration
    """
    config = f"""[Interface]
PrivateKey = {client_private_key}
Address = {client_ip}/32
DNS = {dns_server}

[Peer]
PublicKey = {server_public_key}
Endpoint = {server_endpoint}
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
"""
    return config

def generate_server_config(server_private_key: str, server_port: int,
                          server_ip: str, peers: list) -> str:
    """
    Generate server-side WireGuard configuration
    Peers should be a list of dicts with keys: public_key, allowed_ip
    """
    config = f"""[Interface]
PrivateKey = {server_private_key}
Address = {server_ip}/24
ListenPort = {server_port}
PostUp = iptables -A FORWARD -i %%i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %%i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

"""

    for peer in peers:
        config += f"""[Peer]
PublicKey = {peer["public_key"]}
AllowedIPs = {peer["allowed_ip"]}/32

"""

    return config
