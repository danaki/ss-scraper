# -*- coding: utf-8 -*-

from __future__ import print_function, division

import random

from flask import (Blueprint, request, session, g, redirect, url_for,
     abort, render_template, flash)

from pprint import pprint

from bokeh.charts import defaults, Bar, Scatter, BoxPlot
from bokeh.charts.operations import blend

import datetime as dt
import pandas as pd
import numpy as np
import blaze as bz

from odo import odo

from .common import *
from .forms import *

cars = Blueprint('cars', __name__)

@cars.before_request
def before_request():
    ds = bz.Data(bz.resource('mongodb://localhost/scrapy::car'), dshape="""var * {
            open: bool,
            production_year: int,
            mileage: ?int,
            price: real,
            price_period: ?string,
            url: string,
            brand: string,
            color: string
        }""")

    g.ds = ds[(ds.open == True)
        & (ds.price_period == None)
        & (ds.mileage > 0)
        & (ds.mileage < 1e+6)
        & (ds.production_year > (dt.date.today().year - 20))]

@cars.route("/price-vs-year")
def price_vs_year():
    return _any_vs_year(values='price', title="Price vs Year of production", ylabel="Price, EUR")

@cars.route("/mileage-vs-year")
def mileage_vs_year():
    return _any_vs_year(values='mileage', title="Mileage vs Year of production", ylabel="Mileage, km")

@cars.route("/scatter-price-vs-mileage")
def scatter_price_vs_mileage():
    df = odo(g.ds, pd.DataFrame)

    return render(scatter_any(df, 'mileage', 'price',
        title="Price vs Mileage",
        xlabel="Mileage, km",
        ylabel="Price, EUR"))


@cars.route("/scatter-mileage-vs-year")
def scatter_mileage_vs_year():
    df = odo(g.ds, pd.DataFrame)

    df['jitter_year'] = jitter(list(df['production_year']))

    return render(scatter_any(df, 'jitter_year', 'mileage',
        title="Mileage vs Year of production",
        xlabel="Year",
        ylabel="Mileage, km"))

@cars.route("/bar-price-counts-by-year")
def bar_price_counts_by_year():
    return render(_bar_any_by_year(bz.count,
        title="Total count by Year of production",
        xlabel="Year",
        ylabel="Count"))

@cars.route("/bar-price-sum-by-year")
def bar_price_sum_by_year():
    return render(_bar_any_by_year(bz.sum,
        title="Price sum by Year of production",
        xlabel="Year",
        ylabel="Price sum"))

@cars.route("/bar-price-mean-by-year")
def bar_price_mean_by_year():
    return render(_bar_any_by_year(bz.mean,
        title="Price mean by Year of production",
        xlabel="Year",
        ylabel="Mean price"))

@cars.route("/bar-color-by-year")
def bar_color_by_year():
    df = odo(g.ds, pd.DataFrame)

    df1 = df.groupby(['production_year', 'color']).size().reset_index().rename(columns={0: 'count'})
    sums = df.groupby(['production_year', 'color']).agg('size').reset_index().groupby('production_year').sum()
    df1['prc'] = df1.apply(lambda x: x[2] * 100 / sums.loc[x[0]], axis=1)

    form = CarsRelativeValuesForm(request.args, csrf_enabled=False)

    field = 'prc' if 'submit' in request.args and form.validate() and form.is_relative.data else 'count'

    p = Bar(df1,
        values=field,
        label='production_year',
        stack='color',
        legend='top_right',
        title='Colors by Year of production',
        xlabel="Year",
        ylabel="Count"
        )

    p.background_fill_color = "beige"

    return render(p, dict(form=form))


##########################################################################################


def _bar_any_by_year(func, **kwargs):
    grouping = bz.by(g.ds.production_year, val=func(g.ds.price))

    df = _order_years(grouping)

    p = Bar(df, 'production_year', values='val', **kwargs)
    set_numerical_axis(p)

    return p

def _order_years(grouping):
    fields = grouping.fields
    k = fields[0]
    d = dict(grouping)

    year = g.ds.production_year

    min = bz.compute(year.min())
    max = bz.compute(year.max())

    df = pd.DataFrame(columns=fields)
    for y in xrange(min, max + 1):
        df.loc[y] = (y, d.get(y, 0))

    df[k] = df[k].astype('int64')

    return df

# def jitter(values, limit=1):
#     half = limit / 2
#     return [random.uniform(-half, half) + x for x in values]


def _any_vs_year(values, **kwargs):
    brands = sorted(list(g.ds.brand.distinct()))
    choices = zip(brands, brands)
    choices.insert(0, ('', "* All brands *",))

    form = CarsBrandForm(request.args, csrf_enabled=False)
    form.brand.choices = choices

    ds = g.ds
    plot_kind = 'box'
    if 'submit' in request.args and form.validate():
        if form.brand.data != '':
            ds = ds[ds.brand == form.brand.data]

        plot_kind = form.plot_kind.data

    df = odo(ds, pd.DataFrame)

    if plot_kind == 'box':
        p = BoxPlot(df,
            values=values,
            label='production_year',
            whisker_color='goldenrod',
            xlabel="Year of production",
            outliers=bool(request.args.get('outliers', '')),
            **kwargs)

        # from bokeh.models.tickers import YearsTicker
        # xaxis = p.select(dict(type=Axis, layout="bottom"))
        # xaxis.ticker = YearsTicker()

        set_numerical_axis(p)
    else:
        df['jitter_year'] = jitter(list(df['production_year']))

        p = scatter_any(df, 'jitter_year',
            values,
            xlabel="Year",
            **kwargs)

    return render(p, dict(form=form))
