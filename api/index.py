import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import and run the web server
from web_server import app

# Vercel handler
def handler(request):
    return app(request)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
