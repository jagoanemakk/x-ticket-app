from website import create_app

web = create_app()
if __name__ =='__main__':
    # app.run(debug=True)
    web.run_app(debug=True, host='192.168.3.30', port=5000)
