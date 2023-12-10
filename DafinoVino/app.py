from __init__ import db, create_app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
