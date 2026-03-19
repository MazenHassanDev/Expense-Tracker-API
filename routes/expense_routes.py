from flask import Blueprint, request, jsonify
from utils.database import Session
from models.expense_model import Expense, CategoryEnum
from utils.jwt_authentication import token_required, get_current_user_id
from utils.extensions import limiter
from datetime import datetime, timedelta

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('/expenses', methods=['GET'])
@token_required
@limiter.limit('60 per minute', key_func=get_current_user_id)
def get_expenses(user_id):
    session = Session()

    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        offset = (page - 1) * limit
        filter_type = request.args.get('filter')

        VALID_FILTERS = ['past_week', 'past_month', 'past_3_months', 'custom']

        if filter_type and filter_type not in VALID_FILTERS:
            return jsonify({'message': f'Invalid filter. Must be one of: {VALID_FILTERS}'}), 400

        query = session.query(Expense).filter_by(user_id=user_id)

        if filter_type == 'past_week':
            start_date = datetime.utcnow() - timedelta(weeks=1)
            query = query.filter(Expense.date >= start_date)

        elif filter_type == 'past_month':
            start_date = datetime.utcnow() - timedelta(days=30)
            query = query.filter(Expense.date >= start_date)

        elif filter_type == 'past_3_months':
            start_date = datetime.utcnow() - timedelta(days=90)
            query = query.filter(Expense.date >= start_date)
        
        elif filter_type == 'custom':
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            if not start_date or not end_date:
                return jsonify({'message': 'start_date and end_date are required for custom filter'}), 400

            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD.'}), 400
            
            query = query.filter(Expense.date >= start_date, Expense.date <= end_date)

        total_expenses = query.count()
        expenses = query.order_by(Expense.date.desc()).offset(offset).limit(limit).all()

        return jsonify({
            'data':[
                {
                    'id': expense.id,
                    'title': expense.title,
                    'amount': float(expense.amount),
                    'category': expense.category.value,
                    'date': expense.date.strftime('%Y-%m-%d')
                }
            for expense in expenses],
            'page': page,
            'limit': limit,
            'total': total_expenses
        }), 200
    
    except Exception as e:
        return jsonify({'message': "Something went wrong", 'error': str(e)}), 500
    finally:
        session.close()

@expenses_bp.route('/expenses', methods=['POST'])
@token_required
@limiter.limit('30 per minute', key_func=get_current_user_id)
def create_expense(user_id):
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No input data provided'}), 400
    
    title = data.get('title')
    amount = data.get('amount')
    category = data.get('category')
    description = data.get('description')
    date = data.get('date')

    if not title or not amount or not category or not date:
        return jsonify({'message': 'Missing required fields'}), 400
    
    try:
        category_enum = CategoryEnum[category]
    except KeyError:
        return jsonify({'message': 'Invalid category'}), 400
    
    try:
        date = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD.'}), 400
    
    session = Session()

    try:

        new_expense = Expense(
            title=title,
            amount=amount,
            category=category_enum,
            description=description,
            date=date,
            user_id=user_id
        )

        session.add(new_expense)
        session.commit()

        return jsonify({
            'id': new_expense.id,
            'title': new_expense.title,
            'amount': float(new_expense.amount),
            'category': new_expense.category.value,
            'date': new_expense.date.strftime('%Y-%m-%d')
        }), 201
    
    except Exception as e:
        session.rollback()
        return jsonify({'message': "Something went wrong", 'error': str(e)}), 500
    finally:
        session.close()


@expenses_bp.route('/expenses/<int:expense_id>', methods=['PUT'])
@token_required
@limiter.limit('30 per minute', key_func=get_current_user_id)
def update_expense(user_id, expense_id):
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No input data provided'}), 400
    
    session = Session()

    try:
        expense = session.query(Expense).filter_by(id=expense_id).first()

        if not expense:
            return jsonify({'message': 'Expense not found'}), 404
        
        if expense.user_id != user_id:
            return jsonify({'message': 'Unauthorized'}), 401
        
        if 'category' in data:
            try:
                data['category'] = CategoryEnum[data['category']]
            except KeyError:
                return jsonify({'message': 'Invalid category'}), 400
            
        if 'date' in data:
            try:
                data['date'] = datetime.strptime(data['date'], '%Y-%m-%d')
            except ValueError:
                return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD.'}), 400
        
        expense.title = data.get('title', expense.title)
        expense.amount = data.get('amount', expense.amount)
        expense.category = data.get('category', expense.category)
        expense.description = data.get('description', expense.description)
        expense.date = data.get('date', expense.date)

        session.commit()

        return jsonify({
            'id': expense.id,
            'title': expense.title,
            'amount': float(expense.amount),
            'category': expense.category.value,
            'date': expense.date.strftime('%Y-%m-%d')
        }), 200
    
    except Exception as e:
        session.rollback()
        return jsonify({'message': "Something went wrong", 'error': str(e)}), 500
    finally:
        session.close()

@expenses_bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
@token_required
@limiter.limit('30 per minute', key_func=get_current_user_id)
def delete(user_id, expense_id):
    session = Session()

    try:
        expense = session.query(Expense).filter_by(id=expense_id).first()

        if not expense:
            return jsonify({'message': 'Expense not found'}), 404
        
        if expense.user_id != user_id:
            return jsonify({'message': 'Unauthorized'}), 401
        
        session.delete(expense)
        session.commit()

        return '', 204
    
    except Exception as e:
        session.rollback()
        return jsonify({'message': "Something went wrong", 'error': str(e)}), 500
    finally:
        session.close()
