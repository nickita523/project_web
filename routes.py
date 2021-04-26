from flask import render_template, redirect, url_for, request, flash


@app.route('/', methods=['GET'])
def main():
    return 'hello'


@app.route('/main', methods=['GET'])
def hello():
    return 'eeee'
