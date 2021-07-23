"""Utils module for trivia app."""

from flask import jsonify
from models import Category
from constants import ERROR_MESSAGES


def get_formatted_categories():
    """
    Get all categories formatted.

    :return:
    """
    categories = Category.query.order_by(Category.type).all()
    return {category.id: category.type for category in categories}


def paginated_data(request, queryset, page_limit):
    """
    Get paginated data.

    :param request:
    :param queryset:
    :param page_limit:
    :return:
    """
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * page_limit
    end = start + page_limit

    return [row.format() for row in queryset[start:end]]


def error_response(http_status):
    """
    Get error response based on http status.

    :param http_status:
    :return:
    """
    return jsonify({
        "success": False,
        "error": http_status,
        "message": ERROR_MESSAGES[http_status]
        }), http_status
