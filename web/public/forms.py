from flask_wtf import Form
from wtforms.fields import *


class BoxOrScatterForm(Form):
    plot_kind = RadioField('Show...', choices=[('box', 'Box'), ('scatter', 'Scatter')], default='box')
    submit = SubmitField('Show')

class NoOutliersForm(Form):
    no_outliers = BooleanField(label='No outliers')
    submit = SubmitField('Show')

class CarsBrandForm(BoxOrScatterForm):
    brand = SelectField(label='Brand')
    submit = SubmitField('Show')

class CarsRelativeValuesForm(Form):
    is_relative = BooleanField(label='Relative values')
    submit = SubmitField('Show')

class FlatsNoNewProjectsForm(Form):
    no_new = BooleanField(label='No new projects')
    submit = SubmitField('Show')

