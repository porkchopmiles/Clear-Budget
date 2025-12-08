# -*- coding: utf-8 -*-
"""

@author: miles
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

