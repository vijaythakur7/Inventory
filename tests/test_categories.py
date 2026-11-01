
#################   Understand what we need to test   ###################

def test_create_category(client, monkeypatch):

    def mock_get_current_user(token):

        from types import SimpleNamespace

        return SimpleNamespace(
            ok=True,
            status_code=200,
            json=lambda: {
                "id": 101,
                "name": "Test User",
                "email": "test@example.com"
            }
        )

    monkeypatch.setattr(
        "middleware.authentication.get_current_user",
        mock_get_current_user
    )

    response = client.post(
        "/api/categories",
        json={
            "name": "Electronics",
            "description": "Electronic products"
        },
        headers={
            "Authorization": "Bearer valid-test-token"
        }
    )

    assert response.status_code == 201

    response_data = response.get_json()

    assert response_data["success"] is True
    assert response_data["message"] == "Category created successfully"
    assert response_data["data"]["name"] == "Electronics"
    assert response_data["data"]["description"] == "Electronic products"


###############    Test category retrieval and ownership   #############  

from types import SimpleNamespace

from extensions import db
from models.categories_model import Category


def test_get_categories_by_user(client, monkeypatch):

    def mock_get_current_user(token):

        return SimpleNamespace(
            ok=True,
            status_code=200,
            json=lambda: {
                "id": 101,
                "name": "Test User",
                "email": "test@example.com"
            }
        )

    monkeypatch.setattr(
        "middleware.authentication.get_current_user",
        mock_get_current_user
    )

    # Create categories for two different users
    category1 = Category(
        name="Electronics",
        description="Electronic products",
        user_id=101
    )

    category2 = Category(
        name="Clothing",
        description="Clothing products",
        user_id=202
    )

    db.session.add_all([category1, category2])
    db.session.commit()

    response = client.get(
        "/api/categories",
        headers={
            "Authorization": "Bearer valid-test-token"
        }
    )

    assert response.status_code == 200

    response_data = response.get_json()

    assert response_data["success"] is True
    assert len(response_data["data"]) == 1

    assert response_data["data"][0]["name"] == "Electronics"



######################    Get category by ID     ######################

def test_get_category_by_id(client, monkeypatch):

    def mock_get_current_user(token):
        return SimpleNamespace(
            ok=True,
            status_code=200,
            json=lambda: {"id": 101}
        )

    monkeypatch.setattr(
        "middleware.authentication.get_current_user",
        mock_get_current_user
    )

    category = Category(
        name="Electronics",
        description="Electronic products",
        user_id=101
    )

    db.session.add(category)
    db.session.commit()

    response = client.get(
        f"/api/categories/{category.id}",
        headers={
            "Authorization": "Bearer valid-test-token"
        }
    )

    assert response.status_code == 200

    response_data = response.get_json()

    assert response_data["success"] is True
    assert response_data["data"]["name"] == "Electronics"



#################   Test category ownership security   #################



def test_user_cannot_access_another_users_category(client, monkeypatch):

    def mock_get_current_user(token):
        return SimpleNamespace(
            ok=True,
            status_code=200,
            json=lambda: {"id": 202}
        )

    monkeypatch.setattr(
        "middleware.authentication.get_current_user",
        mock_get_current_user
    )

    # Category belongs to User 101
    category = Category(
        name="Electronics",
        description="Electronic products",
        user_id=101
    )

    db.session.add(category)
    db.session.commit()

    response = client.get(
        f"/api/categories/{category.id}",
        headers={
            "Authorization": "Bearer valid-test-token"
        }
    )

    assert response.status_code == 404

    response_data = response.get_json()

    assert response_data["success"] is False
    assert response_data["message"] == "Category not found"



#################    Category Update Testing     #######################

def test_update_category(client, monkeypatch):

    def mock_get_current_user(token):
        return SimpleNamespace(
            ok=True,
            status_code=200,
            json=lambda: {"id": 101}
        )

    monkeypatch.setattr(
        "middleware.authentication.get_current_user",
        mock_get_current_user
    )

    # Create a category belonging to User 101
    category = Category(
        name="Electronics",
        description="Old description",
        user_id=101
    )

    db.session.add(category)
    db.session.commit()

    # Update the category
    response = client.put(
        f"/api/categories/{category.id}",
        json={
            "name": "Mobile Phones",
            "description": "Smartphones and accessories"
        },
        headers={
            "Authorization": "Bearer valid-test-token"
        }
    )

    assert response.status_code == 200

    response_data = response.get_json()

    assert response_data["success"] is True
    assert response_data["message"] == "Category updated successfully"

    assert response_data["data"]["name"] == "Mobile Phones"

    assert response_data["data"]["description"] == (
        "Smartphones and accessories"
    )



###########  Test that another user cannot update the category ##########


def test_user_cannot_update_another_users_category(
    client,
    monkeypatch
):

    def mock_get_current_user(token):
        return SimpleNamespace(
            ok=True,
            status_code=200,
            json=lambda: {"id": 202}
        )

    monkeypatch.setattr(
        "middleware.authentication.get_current_user",
        mock_get_current_user
    )

    # Category belongs to User 101
    category = Category(
        name="Electronics",
        description="Electronic products",
        user_id=101
    )

    db.session.add(category)
    db.session.commit()

    # User 202 attempts to update User 101's category
    response = client.put(
        f"/api/categories/{category.id}",
        json={
            "name": "Hacked Category"
        },
        headers={
            "Authorization": "Bearer valid-test-token"
        }
    )

    assert response.status_code == 404

    response_data = response.get_json()

    assert response_data["success"] is False
    assert response_data["message"] == "Category not found"

    # Verify original category name remains unchanged
    saved_category = db.session.get(Category, category.id)

    assert saved_category.name == "Electronics"




#####################    Category Delete Testing     ####################




def test_delete_category(client, monkeypatch):

    def mock_get_current_user(token):
        return SimpleNamespace(
            ok=True,
            status_code=200,
            json=lambda: {"id": 101}
        )

    monkeypatch.setattr(
        "middleware.authentication.get_current_user",
        mock_get_current_user
    )

    category = Category(
        name="Electronics",
        description="Electronic products",
        user_id=101
    )

    db.session.add(category)
    db.session.commit()

    category_id = category.id

    response = client.delete(
        f"/api/categories/{category_id}",
        headers={
            "Authorization": "Bearer valid-test-token"
        }
    )

    assert response.status_code == 200

    response_data = response.get_json()

    assert response_data["success"] is True
    assert response_data["message"] == "Category deleted successfully"

    deleted_category = db.session.get(Category, category_id)

    assert deleted_category is None




########   Test preventing another user from deleting a category  #######




def test_user_cannot_delete_another_users_category(
    client,
    monkeypatch
):

    def mock_get_current_user(token):
        return SimpleNamespace(
            ok=True,
            status_code=200,
            json=lambda: {"id": 202}
        )

    monkeypatch.setattr(
        "middleware.authentication.get_current_user",
        mock_get_current_user
    )

    category = Category(
        name="Electronics",
        description="Electronic products",
        user_id=101
    )

    db.session.add(category)
    db.session.commit()

    category_id = category.id

    response = client.delete(
        f"/api/categories/{category_id}",
        headers={
            "Authorization": "Bearer valid-test-token"
        }
    )

    assert response.status_code == 404

    response_data = response.get_json()

    assert response_data["success"] is False
    assert response_data["message"] == "Category not found"

    saved_category = db.session.get(Category, category_id)

    assert saved_category is not None
    assert saved_category.name == "Electronics"
    assert saved_category.user_id == 101



##################  Category Validation Testing  #######################

# Now we'll test invalid inputs and edge cases:

# 1. Create category without a name.
# 2. Create category with an empty name.
# 3. Create category with a name exceeding 100 characters.
# 4. Create category with a description exceeding 255 characters.
# 5. Update category with invalid data.
# 6. Request a category using an invalid ID.


##  1. Create category without a name.

def test_create_category_without_name(client, monkeypatch):

    def mock_get_current_user(token):
        return SimpleNamespace(
            ok=True,
            status_code=200,
            json=lambda: {"id": 101}
        )

    monkeypatch.setattr(
        "middleware.authentication.get_current_user",
        mock_get_current_user
    )

    response = client.post(
        "/api/categories",
        json={
            "description": "Electronic products"
        },
        headers={
            "Authorization": "Bearer valid-test-token"
        }
    )

    assert response.status_code == 400

    response_data = response.get_json()

    assert response_data["success"] is False
    assert response_data["message"] == "Category name is required"


##  2. Create category with an empty name.


def test_create_category_with_empty_name(client, monkeypatch):

    def mock_get_current_user(token):
        return SimpleNamespace(
            ok=True,
            status_code=200,
            json=lambda: {"id": 101}
        )

    monkeypatch.setattr(
        "middleware.authentication.get_current_user",
        mock_get_current_user
    )

    response = client.post(
        "/api/categories",
        json={
            "name": "   ",
            "description": "Electronic products"
        },
        headers={
            "Authorization": "Bearer valid-test-token"
        }
    )

    assert response.status_code == 400

    response_data = response.get_json()

    assert response_data["success"] is False
    assert response_data["message"] == "Category name is required"



## 3. Category name exceeds 100 characters



def test_create_category_name_exceeds_max_length(client, monkeypatch):

    def mock_get_current_user(token):
        return SimpleNamespace(
            ok=True,
            status_code=200,
            json=lambda: {"id": 101}
        )

    monkeypatch.setattr(
        "middleware.authentication.get_current_user",
        mock_get_current_user
    )

    response = client.post(
        "/api/categories",
        json={
            "name": "A" * 101
        },
        headers={
            "Authorization": "Bearer valid-test-token"
        }
    )

    assert response.status_code == 400

    response_data = response.get_json()

    assert response_data["success"] is False
    assert response_data["message"] == (
        "Category name cannot exceed 100 characters"
    )



## 4. Description exceeds 255 characters


def test_create_category_description_exceeds_max_length(
    client,
    monkeypatch
):

    def mock_get_current_user(token):
        return SimpleNamespace(
            ok=True,
            status_code=200,
            json=lambda: {"id": 101}
        )

    monkeypatch.setattr(
        "middleware.authentication.get_current_user",
        mock_get_current_user
    )

    response = client.post(
        "/api/categories",
        json={
            "name": "Electronics",
            "description": "A" * 256
        },
        headers={
            "Authorization": "Bearer valid-test-token"
        }
    )

    assert response.status_code == 400

    response_data = response.get_json()

    assert response_data["success"] is False
    assert response_data["message"] == (
        "Description cannot exceed 255 characters"
    )


## 5.Update category with empty name


def test_update_category_with_empty_name(client, monkeypatch):

    def mock_get_current_user(token):
        return SimpleNamespace(
            ok=True,
            status_code=200,
            json=lambda: {"id": 101}
        )

    monkeypatch.setattr(
        "middleware.authentication.get_current_user",
        mock_get_current_user
    )

    category = Category(
        name="Electronics",
        description="Electronic products",
        user_id=101
    )

    db.session.add(category)
    db.session.commit()

    response = client.put(
        f"/api/categories/{category.id}",
        json={
            "name": "   "
        },
        headers={
            "Authorization": "Bearer valid-test-token"
        }
    )

    assert response.status_code == 400

    response_data = response.get_json()

    assert response_data["success"] is False
    assert response_data["message"] == "Category name is required"

    saved_category = db.session.get(Category, category.id)

    assert saved_category.name == "Electronics"


## 6.Update category with invalid description


def test_update_category_description_exceeds_max_length(
    client,
    monkeypatch
):

    def mock_get_current_user(token):
        return SimpleNamespace(
            ok=True,
            status_code=200,
            json=lambda: {"id": 101}
        )

    monkeypatch.setattr(
        "middleware.authentication.get_current_user",
        mock_get_current_user
    )

    category = Category(
        name="Electronics",
        description="Electronic products",
        user_id=101
    )

    db.session.add(category)
    db.session.commit()

    response = client.put(
        f"/api/categories/{category.id}",
        json={
            "description": "A" * 256
        },
        headers={
            "Authorization": "Bearer valid-test-token"
        }
    )

    assert response.status_code == 400

    response_data = response.get_json()

    assert response_data["success"] is False
    assert response_data["message"] == (
        "Description cannot exceed 255 characters"
    )

    saved_category = db.session.get(Category, category.id)

    assert saved_category.description == "Electronic products"
