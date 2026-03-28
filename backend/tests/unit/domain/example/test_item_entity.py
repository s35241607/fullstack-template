import pytest

from app.domain.example.entities.item import Item
from app.domain.shared.exceptions import BusinessRuleViolationError


class TestItemEntity:
    def test_create_item_with_valid_name(self) -> None:
        item = Item(name="Test Item")
        assert item.name == "Test Item"
        assert item.description == ""
        assert item.id is not None

    def test_create_item_with_description(self) -> None:
        item = Item(name="Test Item", description="A description")
        assert item.description == "A description"

    def test_create_item_with_empty_name_raises_error(self) -> None:
        with pytest.raises(BusinessRuleViolationError):
            Item(name="")

    def test_create_item_with_whitespace_name_raises_error(self) -> None:
        with pytest.raises(BusinessRuleViolationError):
            Item(name="   ")

    def test_create_item_with_name_too_long_raises_error(self) -> None:
        with pytest.raises(BusinessRuleViolationError):
            Item(name="a" * 101)

    def test_update_item_name(self) -> None:
        item = Item(name="Original")
        item.update(name="Updated")
        assert item.name == "Updated"

    def test_update_item_description(self) -> None:
        item = Item(name="Test")
        item.update(description="New description")
        assert item.description == "New description"

    def test_update_item_with_invalid_name_raises_error(self) -> None:
        item = Item(name="Test")
        with pytest.raises(BusinessRuleViolationError):
            item.update(name="")

    def test_items_with_same_id_are_equal(self) -> None:
        item1 = Item(name="Item A")
        item2 = Item.__new__(Item)
        item2.id = item1.id
        item2.name = "Item B"
        item2.description = ""
        assert item1 == item2

    def test_items_with_different_ids_are_not_equal(self) -> None:
        item1 = Item(name="Item A")
        item2 = Item(name="Item A")
        assert item1 != item2
