from flask import jsonify
from models import Category
from constants import ERROR_MESSAGES

def get_formatted_categories():
    categories = Category.query.order_by(Category.type).all()
    return {category.id: category.type for category in categories}


def paginated_data(request, queryset, page_limit):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * page_limit
    end = start + page_limit

    return [row.format() for row in queryset[start:end]]


def error_response(http_status):
    return jsonify({
        "success": False,
        "error": http_status,
        "message": ERROR_MESSAGES[http_status]
        }), http_status