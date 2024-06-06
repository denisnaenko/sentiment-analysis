from analyser import app
from flask import Flask, render_template, redirect, url_for, flash, session, request
from analyser.parser import get_data
from analyser.comment_model_setup import analyse_sentiment
from analyser.forms import ArticleForm, CommentForm

@app.route('/', methods=['GET', 'POST'])
def home_page():
    form = ArticleForm()
    show_data = False

    if request.method == 'POST':
        if form.validate_on_submit():
            article = form.article.data
            feedback = get_data(article)

            if feedback:
                session['show_data'] = True
                # ...
            else:
                flash('Упс, артикул с данным товаром не существует, либо на него нет отзывов!')

        if form.errors != {}:
            for err_msg in form.errors.values():
                flash(f'Артикул должен состоять из цифр!')

        return redirect(url_for('home_page'))

    if request.method == 'GET':
        show_data = session.pop('show_data', False)

        return render_template('index.html', form=form, show_data=show_data)


@app.route('/comments', methods=['GET', 'POST'])
def comments_page():
    form = CommentForm()
    show_data = False
    sentiment = None

    if request.method == 'POST':
        if form.validate_on_submit():
            comment = form.comment.data
            sentiment = analyse_sentiment(comment)

            if sentiment:
                session['show_data'] = True
                session['sentiment'] = sentiment

        return redirect(url_for('comments_page'))

    if request.method == 'GET':
        show_data = session.pop('show_data', False)
        sentiment = session.pop('sentiment', False)

        return render_template('comments.html', form=form, show_data=show_data, sentiment=sentiment)