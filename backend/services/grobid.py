import requests
from backend.core.logging import logger

class GrobidClient:
    def __init__(self, host="localhost", port=8070):
        self.base_url = f"http://{host}:{port}/api"

    def check_health(self):
        # Fix #5: was hardcoded to localhost:8070, now uses self.base_url
        try:
            resp = requests.get(f"{self.base_url}/isalive", timeout=2)
            return resp.status_code == 200
        except Exception:
            return False

    def parse_pdf(self, pdf_path: str):
        """Call Grobid's processFulltextDocument endpoint to extract structured content."""
        try:
            with open(pdf_path, "rb") as f:
                resp = requests.post(
                    f"{self.base_url}/processFulltextDocument",
                    files={"input": f},
                    timeout=120
                )
            if resp.status_code == 200:
                return {"status": "ok", "tei_xml": resp.text}
            else:
                logger.warning(f"Grobid returned status {resp.status_code}")
                return {"status": "error", "detail": resp.text}
        except Exception as e:
            logger.error(f"Grobid parse_pdf failed: {e}")
            return {"status": "error", "detail": str(e)}

grobid_client = GrobidClient()
