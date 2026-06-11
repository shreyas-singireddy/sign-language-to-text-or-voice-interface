"""
SignBridge AI — Layer 12: Emergency System Package
Provides SOS detection, alert dispatching, panic protocol,
and emergency phrase bank for life-critical communication.
"""
from emergency.sos_detector import SOSDetector, sos_detector
from emergency.alert_dispatcher import AlertDispatcher, alert_dispatcher
from emergency.panic_protocol import PanicProtocol, panic_protocol

__all__ = [
    "SOSDetector", "sos_detector",
    "AlertDispatcher", "alert_dispatcher",
    "PanicProtocol", "panic_protocol",
]
