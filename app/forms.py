from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SearchBar(FlaskForm):
	text_box = StringField('Text Box', validators=[DataRequired()])
	search = SubmitField("Search")