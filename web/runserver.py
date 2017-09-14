import os
from app import create_app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    print(__doc__)
    app = create_app("config/dev.py")
    app.run(host='0.0.0.0', port=port)