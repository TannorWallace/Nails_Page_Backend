import pytest

def test_get_all_images(client):
    """GET /images/ should return a list of images"""
    response = client.get("/images/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print(f"✅ Got {len(data)} images")


def test_get_single_image_with_comments(client):
    """GET /images/{id} should return image + its comments"""
    response = client.get("/images/1")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "id" in data
        assert "comments" in data
        assert isinstance(data["comments"], list)