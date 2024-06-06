from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Regexp

class ArticleForm(FlaskForm):
    article = StringField(label='article', validators=[DataRequired(), Regexp(regex='^\d+$')])
    submit = SubmitField(label='Отправить')

class CommentForm(FlaskForm):
    comment = StringField(label='comment', validators=[DataRequired()])
    submit = SubmitField(label='Отправить')