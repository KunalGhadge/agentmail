import os
import uuid
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

class AgentIdentity:
    """
    Handles the sovereign identity of an AI Agent.
    Generates a unique UUID and an RSA keypair for cryptographic trust.
    Now supports a 'Vanity Handle' (e.g., hermes@agentmail).
    """

    def __init__(self, key_dir=".agent_keys", id_file=".agent_id", handle_file=".agent_handle"):
        self.key_dir = key_dir
        self.id_file = id_file
        self.handle_file = handle_file
        self.address = None
        self.handle = None
        self.private_key = None
        self.public_key = None
        
        # We call init() automatically so the student doesn't have to worry about setup
        self.init()

    def init(self):
        """Initializes the identity, generating keys and IDs if they don't exist."""
        # Step 1: Create the directory for our security keys
        os.makedirs(self.key_dir, exist_ok=True)

        # Step 2: Handle the Agent ID (Our "Phone Number")
        if not os.path.exists(self.id_file):
            print(f"[*] Generating new Agent ID...")
            new_id = str(uuid.uuid4())
            with open(self.id_file, "w") as f:
                f.write(new_id)
            self.address = new_id
        else:
            with open(self.id_file, "r") as f:
                self.address = f.read().strip()

        # Step 3: Handle the Vanity Handle (e.g., hermes)
        if os.path.exists(self.handle_file):
            with open(self.handle_file, "r") as f:
                self.handle = f.read().strip()

        # Step 4: Handle the RSA Keypair
        priv_path = os.path.join(self.key_dir, "priv.pem")
        pub_path = os.path.join(self.key_dir, "pub.pem")

        if not os.path.exists(priv_path):
            print(f"[*] Generating new RSA keypair (2048-bit)...")
            # Generate the private key
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            # Save private key to file
            with open(priv_path, "wb") as f:
                f.write(self.private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            # Generate and save the public key
            self.public_key = self.private_key.public_key()
            with open(pub_path, "wb") as f:
                f.write(self.public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ))
        else:
            # Load existing keys from files
            with open(priv_path, "rb") as f:
                self.private_key = serialization.load_pem_private_key(f.read(), password=None)
            with open(pub_path, "rb") as f:
                self.public_key = serialization.load_pem_public_key(f.read())

    def set_handle(self, handle: str):
        """Saves a vanity handle to the agent's identity."""
        self.handle = handle
        with open(self.handle_file, "w") as f:
            f.write(handle)
        print(f"[*] Handle set locally: {handle}")

    def get_full_address(self) -> str:
        """
        Returns the formatted address. 
        If handle exists: handle@agentmail
        Otherwise: the raw UUID
        """
        if self.handle:
            return f"{self.handle}@agentmail"
        return self.address

    def get_address(self) -> str:
        """Returns the raw UUID string."""
        return self.address

    def sign_payload(self, data_string: str) -> str:
        """
        Signs a string using RSA-PSS. 
        Think of this as an 'unforgeable digital signature' only this agent can provide.
        """
        if not self.private_key:
            raise ValueError("Identity not initialized. Call init() first.")

        # Modern RSA-PSS signature
        signature = self.private_key.sign(
            data_string.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Return as Base64 for easy transport in JSON
        return base64.b64encode(signature).decode('utf-8')

# Example usage for our CS Student:
if __name__ == "__main__":
    identity = AgentIdentity()
    print(f"UUID Address: {identity.get_address()}")
    if identity.handle:
        print(f"Vanity Address: {identity.get_full_address()}")
    sig = identity.sign_payload("Hello Agent World!")
    print(f"Signature: {sig[:20]}...")
