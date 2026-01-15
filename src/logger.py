import logging
import re

class SovereignFilter(logging.Filter):
    """Redacts sensitive data from logs automatically"""
    def filter(self, record):
        # Redact any strings that look like IDs or Signatures
        msg = str(record.msg)
        msg = re.sub(r'SOVEREIGN_AUTH_\w+', '[REDACTED_SIG]', msg)
        msg = re.sub(r'norad_id=\d+', 'norad_id=[HIDDEN]', msg)
        record.msg = msg
        return True

def get_sovereign_logger():
    logger = logging.getLogger("KoshaTrack")
    handler = logging.StreamHandler()
    handler.addFilter(SovereignFilter())
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
