from application import app, db

from common.libs.utils import get_current_time
from common.models.member_cart import MemberCart

def set_cart_info(member_id=0, food_id=0, quantity=0):
    if member_id < 1 or food_id < 1 or quantity < 1:
        return None

    cart_info_query = MemberCart.query.filter_by(member_id=member_id, food_id=food_id)

    cart_info = cart_info_query.first()
    if cart_info is None:
        cart_info = MemberCart()
        cart_info.member_id = member_id
        cart_info.food_id = food_id
        cart_info.created_time = get_current_time()
    cart_info.quantity = quantity
    cart_info.updated_time = get_current_time()

    db.session.add(cart_info)
    db.session.commit()

    return cart_info

def delete_cart_info(member_id=0, food_id=0):
    if isinstance(food_id, int):
        if member_id < 1 or food_id < 1:
            return False
        cart_info_query = MemberCart.query.filter_by(member_id=member_id, food_id=food_id)
        if cart_info_query.count() < 1:
            return False
        cart_info_query.delete()
        db.session.commit()
        return True
    elif isinstance(food_id, list):
        if member_id < 1 or len(food_id) < 1:
            return False
        cart_info_query = MemberCart.query.filter(MemberCart.member_id == member_id,
                                                  MemberCart.food_id.in_(food_id))
        count = cart_info_query.count()

        cart_info_query.delete(synchronize_session=False)
        db.session.commit()

        app.logger.debug("member_id %d, list %s, deleted %d items" % (member_id, str(food_id), count))
        return True

def get_cart_quantity(member_id=0, food_id=0):
    if member_id < 1 or food_id < 1:
        return 0
    cart_info =  MemberCart.query.filter_by(member_id=member_id, food_id=food_id).first()
    if cart_info is None:
        return 0
    else:
        return cart_info.quantity