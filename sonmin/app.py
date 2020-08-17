from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/index.html')
def hello_world1():
    return render_template('index.html')


@app.route('/generic.html')
def hello_world2():
    return render_template('generic.html')


@app.route('/elements.html')
def hello_world3():
    return render_template('elements.html')


@app.route('/papago.html')
def hello_world4():
    return render_template('papago.html')


@app.route('/gallery.html')
def hello_world5():
    return render_template('gallery.html')


@app.route('/webcam.html')
def hello_world6():
    return render_template('webcam.html')


if __name__ == '__main__':
    app.run()