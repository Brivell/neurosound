from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
async def health_check(request: Request):
    from main import registry
    return {
        "status": "ok",
        "models_loaded": {
            "yamnet_hub":  "yamnet_hub"  in registry and registry["yamnet_hub"]  is not None,
            "yamnet":      "yamnet"      in registry and registry["yamnet"]      is not None,
            "spectrogram": "spectrogram" in registry and registry["spectrogram"] is not None,
        },
    }
