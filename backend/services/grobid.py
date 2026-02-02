import requests
from backend.core.logging import logger

GROBID_URL = "http://localhost:8070/api/processHeaderDocument"

class GrobidClient:
    def __init__(self, host="localhost", port=8070):
        self.base_url = f"http://{host}:{port}/api"

    def check_health(self):
        try:
            resp = requests.get(f"http://localhost:8070/api/isalive", timeout=2)
            return resp.status_code == 200
        except Exception:
            return False

    # Placeholder for full implementation (extract structure/equations)
    def parse_pdf(self, pdf_path: str):
        # Implementation to call processFulltextDocument
        return {"status": "not_implemented_yet"}

grobid_client = GrobidClient()
