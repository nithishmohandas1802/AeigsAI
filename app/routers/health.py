from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {
        "message": "Welcome to AegisAI 🚀",
        "version": "1.0.0",
        "developer": "Nithish"
    }


@router.get("/health")
def health():  
    return {
        "status": "healthy"
    }