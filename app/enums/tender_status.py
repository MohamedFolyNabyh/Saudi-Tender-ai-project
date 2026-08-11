from enum import Enum

class TenderStatus(str, Enum):

    UPLOADED = "uploaded"

    PROCESSING = "processing"
    

    COMPLETED = "completed"

    FAILED = "failed"