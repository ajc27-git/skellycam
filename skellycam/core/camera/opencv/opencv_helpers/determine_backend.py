import logging
from platform import platform

import cv2
from cv2.videoio_registry import getBackendName
from cv2_enumerate_cameras import supported_backends
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class OpenCVBackend(BaseModel):
    id: int
    name: str

    @classmethod
    def from_backend_id(cls, backend_id: int) -> 'OpenCVBackend':
        name = getBackendName(backend_id)
        if name is None:
            logger.warning(f"Unknown OpenCV backend ID: {backend_id}. Defaulting to cv2.CAP_ANY.")
            backend_id = cv2.CAP_ANY
            name = getBackendName(backend_id)
        return cls(id=backend_id, name=name)


def determine_opencv_camera_backend() -> OpenCVBackend:
    platform_string = platform().lower()
    
    if "windows" in platform_string:
        # Try DSHOW for Windows (could also try MSMF)
        backend = OpenCVBackend.from_backend_id(cv2.CAP_DSHOW)
        logger.debug(f"Windows system detected, using backend: {backend.name}")
        
    elif "linux" in platform().lower():
        # Force V4L2 for Linux USB cameras
        backend = OpenCVBackend.from_backend_id(cv2.CAP_V4L2)
        logger.debug(f"Linux detected, forcing V4L2 backend for USB camera")
        
    else:
        # Unknown system, use ANY
        backend = OpenCVBackend.from_backend_id(cv2.CAP_ANY)
        logger.warning(f"Unknown system: {platform_string}, using backend: {backend.name}")
    
    logger.debug(f"Determined OpenCV backend: {backend.name} (ID: {backend.id})")
    return backend


if __name__ == "__main__":
    b = determine_opencv_camera_backend()
    print(f"OpenCV Backend: {b.name} (ID: {b.id})")
