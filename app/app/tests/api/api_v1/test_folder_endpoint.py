from typing import Dict

from fastapi.testclient import TestClient
from app.core.config import settings
from app.tests.utils.utils import random_lower_string


def test_create_folder(
    client: TestClient, superuser_token_headers: Dict[str, str]
) -> None:
    data = {
        "name": random_lower_string(),
        "description": random_lower_string(),
        "owner": random_lower_string(),
    }
    response = client.post(f"/folders/", headers=superuser_token_headers, json=data)
    assert response.status_code == 201
    content = response.json()
    assert content["name"] == data["name"]
    assert content["description"] == data["description"]
    assert content["owner"] == data["owner"]
    assert "id" in content
    assert "createdAt" in content
    assert "modifiedAt" in content


# def test_create_folder_minimal(client: TestClient, superuser_token_headers: Dict[str, str]) -> None:
#     data = {
#         "name": random_lower_string()
#     }
#     response = client.post(
#         f"/folders/",
#         headers=superuser_token_headers,
#         json=data
#     )
#     assert response.status_code == 200
#     content = response.json()
#     assert content["name"] == data["name"]
#     assert content["description"] == ""
#     assert content["owner"] == ""
#     assert content["products"] == []


# def test_get_folder(client: TestClient, superuser_token_headers: Dict[str, str]) -> None:
#     # First create a folder
#     data = {
#         "name": random_lower_string(),
#         "description": random_lower_string()
#     }
#     create_response = client.post(
#         f"/folders/",
#         headers=superuser_token_headers,
#         json=data
#     )
#     folder_id = create_response.json()["id"]

#     # Then get it
#     response = client.get(
#         f"/folders/{folder_id}",
#         headers=superuser_token_headers
#     )
#     assert response.status_code == 200
#     content = response.json()
#     assert content["name"] == data["name"]
#     assert content["description"] == data["description"]
#     assert content["id"] == folder_id


# def test_get_folder_not_found(client: TestClient, superuser_token_headers: Dict[str, str]) -> None:
#     response = client.get(
#         f"/folders/507f1f77bcf86cd799439011",  # Random MongoDB ObjectId
#         headers=superuser_token_headers
#     )
#     assert response.status_code == 404


# def test_update_folder(client: TestClient, superuser_token_headers: Dict[str, str]) -> None:
#     # First create a folder
#     data = {
#         "name": random_lower_string(),
#         "description": random_lower_string()
#     }
#     create_response = client.post(
#         f"/folders/",
#         headers=superuser_token_headers,
#         json=data
#     )
#     folder_id = create_response.json()["id"]

#     # Then update it
#     update_data = {
#         "name": random_lower_string(),
#         "description": random_lower_string()
#     }
#     response = client.put(
#         f"/folders/{folder_id}",
#         headers=superuser_token_headers,
#         json=update_data
#     )
#     assert response.status_code == 200
#     content = response.json()
#     assert content["name"] == update_data["name"]
#     assert content["description"] == update_data["description"]
#     assert content["id"] == folder_id


# def test_update_folder_partial(client: TestClient, superuser_token_headers: Dict[str, str]) -> None:
#     # First create a folder
#     data = {
#         "name": random_lower_string(),
#         "description": random_lower_string()
#     }
#     create_response = client.post(
#         f"/folders/",
#         headers=superuser_token_headers,
#         json=data
#     )
#     folder_id = create_response.json()["id"]

#     # Then update just the name
#     update_data = {
#         "name": random_lower_string()
#     }
#     response = client.patch(
#         f"/folders/{folder_id}",
#         headers=superuser_token_headers,
#         json=update_data
#     )
#     assert response.status_code == 200
#     content = response.json()
#     assert content["name"] == update_data["name"]
#     assert content["description"] == data["description"]
#     assert content["id"] == folder_id


# def test_delete_folder(client: TestClient, superuser_token_headers: Dict[str, str]) -> None:
#     # First create a folder
#     data = {
#         "name": random_lower_string()
#     }
#     create_response = client.post(
#         f"/folders/",
#         headers=superuser_token_headers,
#         json=data
#     )
#     folder_id = create_response.json()["id"]

#     # Then delete it
#     response = client.delete(
#         f"/folders/{folder_id}",
#         headers=superuser_token_headers
#     )
#     assert response.status_code == 200

#     # Verify it's deleted
#     get_response = client.get(
#         f"/folders/{folder_id}",
#         headers=superuser_token_headers
#     )
#     assert get_response.status_code == 404


# def test_get_folders(client: TestClient, superuser_token_headers: Dict[str, str]) -> None:
#     # Create multiple folders
#     for _ in range(3):
#         data = {
#             "name": random_lower_string()
#         }
#         client.post(
#             f"/folders/",
#             headers=superuser_token_headers,
#             json=data
#         )

#     # Get all folders
#     response = client.get(
#         f"/folders/",
#         headers=superuser_token_headers
#     )
#     assert response.status_code == 200
#     content = response.json()
#     assert "items" in content
#     assert "total" in content
#     assert len(content["items"]) > 0
#     assert content["total"] > 0
