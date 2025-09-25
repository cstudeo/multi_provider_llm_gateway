"""
Flask API Application

This module provides REST API endpoints for the multi-provider LLM interface
with distributed rate limiting.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import traceback
import os
from llm_service import LLMService
from rate_limiter.limiter import RateLimitExceededException
from config import Config

app = Flask(__name__, static_folder='frontend/build/static')
CORS(app)

llm_service = LLMService()

@app.route('/providers', methods=['GET'])
def get_providers():
    """Get list of available providers"""
    try:
        providers = llm_service.get_available_providers()
        return jsonify({
            'providers': providers,
            'count': len(providers)
        })
    except Exception as e:
        return jsonify({
            'error': 'Failed to get providers',
            'message': str(e)
        }), 500

@app.route('/generate', methods=['POST'])
def generate():
    """
    Generate text using specified provider
    
    Request body:
    {
        "provider": "openai|anthropic|google",
        "prompt": "Your prompt here",
        "user_id": "optional_user_id",
        "model": "optional_model_name",
        "max_tokens": 1000,
        "temperature": 0.7
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        if 'provider' not in data:
            return jsonify({'error': 'provider is required'}), 400
        if 'prompt' not in data:
            return jsonify({'error': 'prompt is required'}), 400
        
        provider = data['provider']
        prompt = data['prompt']
        user_id = data.get('user_id')
        
        llm_params = {}
        for param in ['model', 'max_tokens', 'temperature']:
            if param in data:
                llm_params[param] = data[param]
        
        response = llm_service.generate(provider, prompt, user_id, **llm_params)
        
        return jsonify({
            'success': True,
            'response': {
                'content': response.content,
                'provider': response.provider,
                'model': response.model,
                'usage': response.usage,
                'metadata': response.metadata
            }
        })
        
    except RateLimitExceededException as e:
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': str(e),
            'rate_limit_info': e.rate_limit_info
        }), 429
        
    except ValueError as e:
        return jsonify({
            'error': 'Invalid request',
            'message': str(e)
        }), 400
        
    except Exception as e:
        app.logger.error(f"Generation error: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Generation failed',
            'message': str(e)
        }), 500

@app.route('/rate-limit/<provider>', methods=['GET'])
def get_rate_limit_status(provider):
    """Get rate limit status for a provider"""
    try:
        user_id = request.args.get('user_id')
        status = llm_service.get_rate_limit_status(provider, user_id)
        
        return jsonify({
            'provider': provider,
            'user_id': user_id,
            'rate_limits': status
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get rate limit status',
            'message': str(e)
        }), 500


@app.route('/rate-limit/reset/<provider>', methods=['POST'])
def reset_rate_limit(provider):
    """Reset rate limit for a provider (admin endpoint)"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        
        if llm_service.rate_limiter:
            # Reset global rate limit
            global_key = f"global:{user_id}" if user_id else "global"
            llm_service.rate_limiter.reset(global_key, 'global')
            
            # Reset provider-specific rate limit
            provider_key = f"{provider}:{user_id}" if user_id else provider
            llm_service.rate_limiter.reset(provider_key, provider)
        
        return jsonify({
            'success': True,
            'message': f'Rate limits reset for provider {provider}'
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to reset rate limit',
            'message': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        'error': 'Method not allowed',
        'message': 'The HTTP method is not allowed for this endpoint'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    """Serve the React application"""
    if path != "" and os.path.exists(os.path.join('frontend/build', path)):
        return send_from_directory('frontend/build', path)
    else:
        return send_from_directory('frontend/build', 'index.html')


if __name__ == '__main__':
    if not Config.validate_config():
        print("Configuration validation failed. Please check your environment variables.")
        exit(1)
    
    print(f"Starting LLM Interface API on {Config.FLASK_HOST}:{Config.FLASK_PORT}")
    print(f"Available providers: {', '.join(llm_service.get_available_providers())}")
    
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )
