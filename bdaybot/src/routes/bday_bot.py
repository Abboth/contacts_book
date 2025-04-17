from fastapi import APIRouter

router = APIRouter(prefix="/bot", tags=["bot"])

@router.get("/")
async def show_all_persons():
    pass

@router.get("/{person_id}")
async def get_person():
    pass

@router.post("/")
async def add_person():
    pass

@router.put("/{person_id}")
async def update_person():
    pass

@router.delete("/{person_id}")
async def delete_person():
    pass