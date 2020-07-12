from application import db
from common.libs.utils import get_current_time

from common.models.food import Food
from common.models.food_stock_change_log import FoodStockChangeLog

def set_food_stock_change_log(food_id, old_stock, change, note):
    if food_id < 1:
        return False

    stock_change_info = FoodStockChangeLog()
    stock_change_info.food_id = food_id
    stock_change_info.unit = change
    stock_change_info.total_stock = int(old_stock) + int(change)
    stock_change_info.note = note
    stock_change_info.created_time = get_current_time()
    db.session.add(stock_change_info)
    db.session.commit()
    return True