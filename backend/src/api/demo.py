from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ..engine.demo_model import predict
from ..engine.demo_validation import validate

router = APIRouter(prefix="/api/v1/demo", tags=["demo"])


class DemoRequest(BaseModel):
    answers: dict[str, str | int | float | None]


@router.post("/predict")
def demo_predict(req: DemoRequest):
    # Stateless: no DB session, no logging of answers.
    return predict({k: v for k, v in req.answers.items() if v is not None})


@router.post("/assess")
def demo_assess(req: DemoRequest):
    """Validate the chat questionnaire (q1..q10), then classify. Stateless: nothing is stored."""
    clean, errors = validate({k: v for k, v in req.answers.items() if v is not None})
    if errors:
        return JSONResponse(status_code=422, content={"errors": errors})
    return predict({k: v for k, v in clean.items()})
