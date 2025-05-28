from fastapi import HTTPException, Depends
from odmantic import ObjectId
from app import crud
from app.api import deps
from motor.core import AgnosticDatabase
from app.api.auth import APIUser, get_current_user, check_access_permission


# Reusing validation helpers from SoV code
async def validate_and_get_object_id(
    id_str: str, resource_type: str = "resource"
) -> ObjectId:
    """Helper function to validate and convert string ID to ObjectId"""
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=f"'{id_str}' is not a valid {resource_type} ID. It must be a 24-character hex string.",
        )


async def validate_product_access(
    product_id: str,
    db: AgnosticDatabase = Depends(deps.get_db),
    current_user: APIUser = Depends(get_current_user),
) -> ObjectId:
    """Validate product exists and user has access to it"""
    product_object_id = await validate_and_get_object_id(product_id, "product")

    try:
        await check_access_permission(db, current_user, product_id=product_object_id)
    except HTTPException as e:
        if e.status_code == 403:
            raise HTTPException(
                status_code=403,
                detail=f"You don't have permission to access product {product_id}",
            )
        raise e

    product = await crud.products.get(db, id=product_object_id)
    if not product:
        raise HTTPException(
            status_code=404, detail=f"Product with ID '{product_id}' not found"
        )
    return product_object_id
