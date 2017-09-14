from __future__ import division

import random

from flask import Blueprint, render_template

from bokeh.charts import defaults
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.util.string import encode_utf8
from bokeh.resources import INLINE
from bokeh.models import ColumnDataSource, NumeralTickFormatter, Axis, TapTool, OpenURL
from bokeh.palettes import brewer

def render(p, d={}):
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    script, div = components(p, INLINE)
    html = render_template(
        'chart.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
        **d
    )

    return encode_utf8(html)

def set_numerical_axis(p):
    yaxis = p.select(dict(type=Axis, layout="left"))[0]
    yaxis.formatter = NumeralTickFormatter()

def scatter_any(df, x, y, xlabel=None, ylabel=None, color_field=None, xformatter=NumeralTickFormatter(), yformatter=NumeralTickFormatter(), **kwargs):
    f = figure(tools="wheel_zoom,pan,tap", webgl=True, width=defaults.plot_width, height=defaults.plot_height, **kwargs)

    f.xaxis[0].formatter = xformatter
    f.yaxis[0].formatter = yformatter

    f.xaxis.axis_label = xlabel
    f.yaxis.axis_label = ylabel

    taptool = f.select(type=TapTool)
    taptool.callback = OpenURL(url='@url')

    if color_field:
        uniques = sorted(df[color_field].unique())
        # colors = brewer["PiYG"][len(uniques)]
        dark2 = ["#1B9E77", "#D95F02", "#7570B3", "#E7298A", "#66A61E", "#E6AB02", "#A6761D", "#666666"]

        for i, u in enumerate(uniques):
            sdf = df[df[color_field] == u]
            f.scatter(x, y, source=ColumnDataSource(sdf), color=dark2[i], legend=str(u))
    else:
        f.scatter(x, y, source=ColumnDataSource(df))

    return f

def jitter(values, limit=1):
    half = limit / 2
    print(half)
    return [random.uniform(-half, half) + x for x in values]
