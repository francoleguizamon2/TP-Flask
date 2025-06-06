from application import create_app

app = create_app()

@app.route('/main')
def main():
    return 'Hello world'

if __name__ == "__main__":
    app.run(debug=True)

