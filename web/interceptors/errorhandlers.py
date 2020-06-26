from application import app

@app.errorhandler(404)
def page_not_found(error):
    app.logger.error(error)
    return "This page does not exist", 404