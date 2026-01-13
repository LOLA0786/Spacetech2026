import xml.etree.ElementTree as ET
from datetime import datetime

class CDMGenerator:
    @staticmethod
    def generate_xml(object_a, object_b, tca, miss_distance, pc):
        """
        Generates a simplified CCSDS-compliant XML CDM.
        """
        root = ET.Element("cdm", xmlns="urn:ccsds:schema:cdmxml")
        
        header = ET.SubElement(root, "header")
        ET.SubElement(header, "CREATION_DATE").text = datetime.utcnow().isoformat()
        ET.SubElement(header, "ORIGINATOR").text = "SPACETECH_2026_SOC"

        body = ET.SubElement(root, "body")
        
        # Relative Metadata
        rel_metadata = ET.SubElement(body, "relativeMetadataData")
        ET.SubElement(rel_metadata, "TCA").text = tca
        ET.SubElement(rel_metadata, "MISS_DISTANCE").text = f"{miss_distance:.3f}"
        ET.SubElement(rel_metadata, "COLLISION_PROBABILITY").text = f"{pc:.8f}"
        
        # Object Data (Object 1 - Your Sat)
        obj1 = ET.SubElement(body, "segment")
        metadata1 = ET.SubElement(obj1, "metadata")
        ET.SubElement(metadata1, "OBJECT_NAME").text = object_a['name']
        ET.SubElement(metadata1, "OBJECT_ID").text = object_a['id']
        
        # Object Data (Object 2 - Threat)
        obj2 = ET.SubElement(body, "segment")
        metadata2 = ET.SubElement(obj2, "metadata")
        ET.SubElement(metadata2, "OBJECT_NAME").text = object_b['name']
        ET.SubElement(metadata2, "OBJECT_ID").text = object_b['id']

        return ET.tostring(root, encoding='unicode')
