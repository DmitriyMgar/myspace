"""
Обработчики ошибок
"""
from flask import render_template, request, jsonify

def register_error_handlers(app):
    """
    Регистрирует обработчики ошибок
    
    Args:
        app: Экземпляр приложения Flask
    """
    @app.errorhandler(400)
    def bad_request_error(error):
        """Обработчик ошибки 400 Bad Request"""
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'error': 'Bad Request'}), 400
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        """Обработчик ошибки 401 Unauthorized"""
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'error': 'Unauthorized'}), 401
        return render_template('errors/401.html'), 401
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Обработчик ошибки 403 Forbidden"""
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'error': 'Forbidden'}), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Обработчик ошибки 404 Not Found"""
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'error': 'Not Found'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(405)
    def method_not_allowed_error(error):
        """Обработчик ошибки 405 Method Not Allowed"""
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'error': 'Method Not Allowed'}), 405
        return render_template('errors/405.html'), 405
    
    @app.errorhandler(429)
    def too_many_requests_error(error):
        """Обработчик ошибки 429 Too Many Requests"""
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'error': 'Too Many Requests'}), 429
        return render_template('errors/429.html'), 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Обработчик ошибки 500 Internal Server Error"""
        app.logger.error(f'Server Error: {error}')
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'error': 'Internal Server Error'}), 500
        return render_template('errors/500.html'), 500 