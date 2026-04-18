import os
import uuid
import json
from datetime import datetime, timezone
from supabase import create_client, Client
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

class MailStorage:
    """
    Handles persistence of agent messages using a Global Supabase Database.
    Now includes a Registry for 'Vanity Handles' (e.g., hermes@agentmail).
    """

    def __init__(self, url=None, key=None):
        # Allow passing args directly or falling back to environment variables
        self.url = url or os.environ.get("SUPABASE_URL")
        self.key = key or os.environ.get("SUPABASE_KEY")
        
        if not self.url or not self.key:
            raise ValueError("Supabase URL and Key must be provided in .env or constructor.")

        # Initialize the Supabase Client
        self.db: Client = create_client(self.url, self.key)

    # --- REGISTRY METHODS (The 'DNS' of AgentMail) ---

    def resolve_handle(self, handle: str) -> str:
        """
        Converts a vanity handle (e.g., 'hermes') into a raw UUID.
        Returns the UUID string if found, else None.
        """
        try:
            # Check the 'registry' table for the handle mapping
            response = self.db.table("registry").select("uuid").eq("handle", handle).execute()
            if response.data:
                return response.data[0].get("uuid")
            return None
        except Exception as e:
            print(f"[!] Registry Resolve Error: {str(e)}")
            return None

    def register_handle(self, handle: str, uuid_str: str) -> bool:
        """
        Attempts to register a handle to a specific UUID.
        Returns True if successful, False if handle is taken.
        """
        try:
            # Check if handle exists
            existing = self.resolve_handle(handle)
            if existing:
                return False
            
            # Map the handle to the UUID globally
            self.db.table("registry").insert({
                "handle": handle,
                "uuid": uuid_str
            }).execute()
            
            print(f"[*] Global Registry: Registered '{handle}' -> {uuid_str[:8]}...")
            return True
        except Exception as e:
            print(f"[!] Registry Registration Error: {str(e)}")
            return False

    # --- MESSAGE METHODS ---

    def save_message(self, to_addr: str, payload_dict: dict, signature: str, from_addr: str, is_sent=False):
        """Records a new message to the cloud storage."""
        table_name = "sent" if is_sent else "inbox"
        
        data = {
            "id": str(uuid.uuid4()),
            "from_addr": from_addr,
            "to_addr": to_addr,
            "payload": payload_dict,
            "signature": signature
        }
        
        try:
            self.db.table(table_name).insert(data).execute()
            db_name = table_name.upper()
            print(f"[*] Message synced to CLOUD {db_name}: {data['id'][:8]}... -> {to_addr[:8]}...")
        except Exception as e:
            print(f"[!] Cloud Sync Error: {str(e)}")
            raise e

    def get_inbox(self, my_address: str) -> list:
        """Retrieves and clears messages from the cloud inbox."""
        try:
            response = self.db.table("inbox").select("*").eq("to_addr", my_address).execute()
            messages = response.data
            
            if not messages:
                return []

            for msg in messages:
                msg_id = msg.get("id")
                if msg_id:
                    self.db.table("inbox").delete().eq("id", msg_id).execute()
            
            return messages
        except Exception as e:
            print(f"[!] Cloud Retrieval Error: {str(e)}")
            return []

    def get_sent_history(self, from_addr: str) -> list:
        """Retrieves permanent sent history."""
        try:
            response = self.db.table("sent") \
                .select("*") \
                .eq("from_addr", from_addr) \
                .order("ts", desc=True) \
                .execute()
            return response.data
        except Exception as e:
            print(f"[!] Cloud History Error: {str(e)}")
            return []

    def delete_messages(self, msg_id_list: list):
        """Internal interface compatibility for GSD v0.1.0."""
        pass

if __name__ == "__main__":
    # Local Test of Storage Logic
    storage = MailStorage()
    print("Storage client connected.")
