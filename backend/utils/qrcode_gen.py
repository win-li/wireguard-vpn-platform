import qrcode
import io
import base64
from typing import Optional

class QRCodeGenerator:
    """Generate QR codes for WireGuard configurations"""
    
    @staticmethod
    def generate_wireguard_config(
        private_key: str,
        address: str,
        dns: str = "1.1.1.1",
        peer_public_key: str = None,
        peer_endpoint: str = None,
        allowed_ips: str = "0.0.0.0/0",
        keepalive: int = 25
    ) -> str:
        """Generate WireGuard configuration string"""
        config = f"""[Interface]
PrivateKey = {private_key}
Address = {address}
DNS = {dns}

[Peer]
PublicKey = {peer_public_key}
Endpoint = {peer_endpoint}
AllowedIPs = {allowed_ips}
PersistentKeepalive = {keepalive}
"""
        return config
    
    @staticmethod
    def generate_qr_code(
        data: str,
        fill_color: str = "black",
        back_color: str = "white",
        box_size: int = 10,
        border: int = 4
    ) -> io.BytesIO:
        """Generate QR code image from data"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        
        # Save to BytesIO
        img_buffer = io.BytesIO()
        img.save(img_buffer, "PNG")
        img_buffer.seek(0)
        
        return img_buffer
    
    @staticmethod
    def generate_wireguard_qr_base64(
        private_key: str,
        address: str,
        peer_public_key: str,
        peer_endpoint: str,
        dns: str = "1.1.1.1",
        allowed_ips: str = "0.0.0.0/0",
        keepalive: int = 25
    ) -> str:
        """Generate WireGuard QR code as base64 string"""
        config = QRCodeGenerator.generate_wireguard_config(
            private_key=private_key,
            address=address,
            dns=dns,
            peer_public_key=peer_public_key,
            peer_endpoint=peer_endpoint,
            allowed_ips=allowed_ips,
            keepalive=keepalive
        )
        
        img_buffer = QRCodeGenerator.generate_qr_code(config)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode("utf-8")
        
        return img_base64
    
    @staticmethod
    def generate_wireguard_qr_png(
        private_key: str,
        address: str,
        peer_public_key: str,
        peer_endpoint: str,
        dns: str = "1.1.1.1",
        allowed_ips: str = "0.0.0.0/0",
        keepalive: int = 25
    ) -> io.BytesIO:
        """Generate WireGuard QR code as PNG BytesIO"""
        config = QRCodeGenerator.generate_wireguard_config(
            private_key=private_key,
            address=address,
            dns=dns,
            peer_public_key=peer_public_key,
            peer_endpoint=peer_endpoint,
            allowed_ips=allowed_ips,
            keepalive=keepalive
        )
        
        return QRCodeGenerator.generate_qr_code(config)


def create_wireguard_qr(
    private_key: str,
    address: str,
    peer_public_key: str,
    peer_endpoint: str,
    **kwargs
) -> io.BytesIO:
    """Convenience function to create WireGuard QR code"""
    return QRCodeGenerator.generate_wireguard_qr_png(
        private_key=private_key,
        address=address,
        peer_public_key=peer_public_key,
        peer_endpoint=peer_endpoint,
        **kwargs
    )
