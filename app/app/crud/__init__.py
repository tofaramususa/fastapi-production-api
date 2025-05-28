from .crud_user import user
from .crud_folders import folder
from .crud_products import products
from .crud_permissions import folder_permissions

# For a new basic set of CRUD operations you could just do

# from .base import CRUDBase
# from app.models.item import Item
# from app.schemas.item import ItemCreate, ItemUpdate

# item = CRUDBase[Item, ItemCreate, ItemUpdate](Item)
