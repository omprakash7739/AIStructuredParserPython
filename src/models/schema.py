from typing import List
from pydantic import BaseModel, Field


class NutritionInfo(BaseModel):
    """
    Object structure for nutrition information of any menu item
    """
    calories: float | str | None= Field(description="value of calories content in this particular menu item. this field will always content numeric value or N/A if no data found in string format")
    protein_g: float | str | None= Field(description="value of protein content in this particular menu item. this field will always content numeric value or N/A if no data found in string format")
    fat_g: float | str | None = Field(description="value of fat content in this particular menu item. this field will always content numeric value or N/A if no data found in string format")
    carbs_g: float | str | None = Field(description="value of carbohydrate content in this particular menu item. this field will always content numeric value or N/A if no data found in string format")


class MenuItem(BaseModel):
    """
    This is object structure for nutrition information of any restaurant menu items
    """
    name: str = Field(description="name of the  menu item being parsed.")
    nutrition: NutritionInfo = Field(description="collect the nutrition information of the corresponding menu item")


class RestaurantMenu(BaseModel):
    """
    This is object structure for the restaurant menu. This will contains list of items part of the restaurant menu along
    with their nutrition information in prescribed format.
    """
    source: str = Field(description="find the name of the restaurant for which menu items has been provided."
                                    " Generally name of the restaurant will be mentioned on the first 3 paragraph.")
    items: List[MenuItem] = Field(description="collect all the available menu items with their corresponding nutrition "
                                              "information. provide a list output and store it in this items field")

