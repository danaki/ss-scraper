
from bokeh.charts import defaults

from .nav import nav
from .main import main
from .cars import cars
from .flats import flats

__all__ = ['nav', 'main', 'cars', 'flats']

defaults.plot_width = 1140
defaults.plot_height = 800
