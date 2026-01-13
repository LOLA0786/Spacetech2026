from typing import Dict, Any
from datetime import datetime
import xml.etree.ElementTree as ET

def _el(parent, tag, text=None, **attrs):
    e = ET.SubElement(parent, tag, **{k:str(v) for k,v in attrs.items()})
    if text is not None:
        e.text = str(text)
    return e

def export_cdm_xml(event: Dict[str, Any]) -> str:
    """
    Minimal CCSDS-like CDM XML exporter.
    Not full schema validation, but NASA/CDM readable structure.
    """

    root = ET.Element("CDM", attrib={
        "xmlns": "urn:ccsds:schema:ndm-xml"
    })

    header = _el(root, "header")
    _el(header, "CREATION_DATE", event.get("created_at", datetime.utcnow().isoformat()))
    _el(header, "ORIGINATOR", "KOSHA_TRACK")

    body = _el(root, "body")
    meta = _el(body, "metadata")
    _el(meta, "EVENT_ID", event["event_id"])
    _el(meta, "TCA", event.get("tca_utc", "UNKNOWN"))
    _el(meta, "MISS_DISTANCE_KM", event.get("miss_distance_km", 0.0))
    _el(meta, "REL_SPEED_KMS", event.get("rel_speed_kms", 0.0))
    _el(meta, "COLLISION_PROBABILITY", event.get("pc", 0.0))
    _el(meta, "RISK_LEVEL", event.get("risk", "LOW"))

    obj1 = _el(body, "object", id="OBJECT1")
    _el(obj1, "OBJECT_ID", event["object1"]["object_id"])
    _el(obj1, "SOURCE", event["object1"].get("source", "UNKNOWN"))

    st1 = _el(obj1, "stateVector")
    p1 = event["object1"]["state"]["position"]
    v1 = event["object1"]["state"]["velocity"]
    _el(st1, "X_KM", p1["x"]); _el(st1, "Y_KM", p1["y"]); _el(st1, "Z_KM", p1["z"])
    _el(st1, "VX_KMS", v1["vx"]); _el(st1, "VY_KMS", v1["vy"]); _el(st1, "VZ_KMS", v1["vz"])

    obj2 = _el(body, "object", id="OBJECT2")
    _el(obj2, "OBJECT_ID", event["object2"]["object_id"])
    _el(obj2, "SOURCE", event["object2"].get("source", "UNKNOWN"))

    st2 = _el(obj2, "stateVector")
    p2 = event["object2"]["state"]["position"]
    v2 = event["object2"]["state"]["velocity"]
    _el(st2, "X_KM", p2["x"]); _el(st2, "Y_KM", p2["y"]); _el(st2, "Z_KM", p2["z"])
    _el(st2, "VX_KMS", v2["vx"]); _el(st2, "VY_KMS", v2["vy"]); _el(st2, "VZ_KMS", v2["vz"])

    xml_bytes = ET.tostring(root, encoding="utf-8")
    return xml_bytes.decode("utf-8")
