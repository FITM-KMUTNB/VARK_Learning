from varkapp import app, manager

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8081)
    #manager.run()