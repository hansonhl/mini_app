from flask import Blueprint, request, make_response, redirect
from sqlalchemy import or_

from common.libs.utils import render_template_with_global_vars, pagination, json_response, json_error_response, \
    get_current_time
from common.libs.url_utils import build_url
from common.models.member import Member

from application import app, db


member_blueprint = Blueprint("member", __name__)

@member_blueprint.route("/index")
def index():
    current_page = int(request.args.get("p", "1"))
    values = request.values
    items_per_page = app.config["ACCOUNT_INDEX_ITEMS_PER_PAGE"]

    member_info_query = Member.query.order_by(Member.status.desc(), Member.id.desc())
    app.logger.debug("number of members: %d" % member_info_query.count())
    # filtering by search
    if "mix_kw" in values and len(values["mix_kw"]) > 0:
        app.logger.debug("mix_kw %s" % values["mix_kw"])
        rule = or_(Member.nickname.ilike("%%%s%%" % values["mix_kw"]),
                   Member.mobile.ilike("%%%s%%" % values["mix_kw"]))
        member_info_query = member_info_query.filter(rule)

    if "status" in values:
        if values["status"] != "-1":
            member_info_query = member_info_query.filter_by(status=int(values["status"]))

    # pagination
    offset = (current_page - 1) * items_per_page
    pagination_dict = pagination(num_items=member_info_query.count(),
                                 items_per_page=items_per_page,
                                 current_page=current_page,
                                 url=build_url("/member/index?"))
    member_info_list = member_info_query.offset(offset).limit(items_per_page).all()

    page_params = {"member_info_list": member_info_list,
                   "pagination": pagination_dict,
                   "search": {"mix_kw": values.get("mix_kw", None),
                              "status": values.get("status", "-1")},
                   "status_mapping": app.config["ACCOUNT_STATUS_MAPPING"]}

    return render_template_with_global_vars("member/index.html", context=page_params)

@member_blueprint.route("/info")
def info():
    id = int(request.args.get("id", "0"))
    redir_response = make_response(redirect(build_url("/member/index")))
    if id == 0:
        return redir_response
    member_info = Member.query.filter_by(id=id).first()
    if member_info is None:
        return redir_response

    return render_template_with_global_vars("member/info.html", context={"member": member_info})

@member_blueprint.route("/set", methods=["GET", "POST"])
def set():
    if request.method == "GET":
        id = int(request.args.get("id", "0"))
        redir_response = make_response(redirect(build_url("/member/index")))
        if id == 0:
            return redir_response
        member_info = Member.query.filter_by(id=id).first()
        if member_info is None:
            return redir_response
        return render_template_with_global_vars("member/set.html", context={"member": member_info})

    elif request.method == "POST":
        id = int(request.form.get("id", "0"))
        if id == 0:
            return json_error_response("该用户不存在，请确认用户id！")
        member_info = Member.query.filter_by(id=id).first()
        if member_info is None:
            return json_error_response("该用户不存在，请确认用户id！")

        new_nickname = request.form.get("nickname", "")
        if len(new_nickname) < 1:
            return json_error_response("会员名称不能为空！")

        member_info.nickname = new_nickname
        member_info.update_time = get_current_time()
        db.session.add(member_info)
        db.session.commit()
        return json_response("修改会员信息成功！")

@member_blueprint.route("/ops", methods=["POST"])
def ops():
    values = request.form
    if "act" not in values or "id" not in values:
        return json_error_response("无效的账号编辑操作")

    member_info = Member.query.filter_by(id=values["id"]).first()

    if not member_info:
        return json_error_response("无效的账号编辑操作")

    if values["act"] == "remove":
        member_info.status = 0
        success_msg = "成功移除 %s 的账户" % (member_info.nickname)
    elif values["act"] == "recover":
        success_msg = "成功恢复 %s 的账户" % (member_info.nickname)
        member_info.status = 1
    else:
        return json_error_response("无效的账号编辑操作")

    member_info.update_time = get_current_time()

    db.session.add(member_info)
    db.session.commit()

    return json_response(success_msg)


@member_blueprint.route("/comment")
def comment():
    return render_template_with_global_vars("member/comment.html")