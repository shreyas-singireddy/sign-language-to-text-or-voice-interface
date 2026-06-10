import collections
import sys
import numpy as np
from config.logger import setup_logger

logger = setup_logger("ai_engine.temporal_memory")

class TemporalMemory:
    def __init__(self):
        # Rolling buffers for different analysis window intervals
        self.buffer_30 = collections.deque(maxlen=30)
        self.buffer_60 = collections.deque(maxlen=60)
        self.buffer_120 = collections.deque(maxlen=120)

    def memorize(self, feature_record: dict):
        """
        Pushes a new processed frame record into all temporal buffers.
        """
        # Save a compact version (coordinates + key indicators)
        compact_record = {
            "landmarks": feature_record.get("landmarks", []),
            "mean_velocity": feature_record.get("mean_velocity", 0.0),
            "mean_acceleration": feature_record.get("mean_acceleration", 0.0),
            "stability_index": feature_record.get("stability_index", 1.0)
        }
        
        self.buffer_30.append(compact_record)
        self.buffer_60.append(compact_record)
        self.buffer_120.append(compact_record)

    def get_memory_stats(self) -> dict:
        """
        Computes memory occupancy metrics.
        """
        # Calculate memory footprint in bytes
        size_30 = sys.getsizeof(self.buffer_30) + sum(sys.getsizeof(r) for r in self.buffer_30)
        size_60 = sys.getsizeof(self.buffer_60) + sum(sys.getsizeof(r) for r in self.buffer_60)
        size_120 = sys.getsizeof(self.buffer_120) + sum(sys.getsizeof(r) for r in self.buffer_120)
        
        total_kb = (size_30 + size_60 + size_120) / 1024.0

        return {
            "buffer_30_size": len(self.buffer_30),
            "buffer_60_size": len(self.buffer_60),
            "buffer_120_size": len(self.buffer_120),
            "memory_usage_kb": round(total_kb, 3),
            "is_ready_30": len(self.buffer_30) >= 30,
            "is_ready_60": len(self.buffer_60) >= 60,
            "is_ready_120": len(self.buffer_120) >= 120
        }

    def clear(self):
        """Resets all buffers."""
        self.buffer_30.clear()
        self.buffer_60.clear()
        self.buffer_120.clear()
        logger.info("Temporal memory buffers cleared.")

temporal_memory = TemporalMemory()
