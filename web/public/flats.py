# -*- coding: utf-8 -*-

from __future__ import print_function, division

from flask import (Blueprint, request, session, g, redirect, url_for,
     abort, render_template, flash)

from bokeh.charts import defaults, Bar, Scatter, BoxPlot
from bokeh.charts.operations import blend, stack
from bokeh.charts.attributes import cat

from bokeh.models import LogTickFormatter, NumeralTickFormatter
from bokeh.models.tickers import LogTicker

from unidecode import unidecode

import pandas as pd
import blaze as bz

from odo import odo

from .common import *
from .forms import *

from pprint import pprint

PROJECT_EPOCHS = {
    u"103.": "USSR",
    u"Staļina": "Other",
    u"Specpr.": "USSR",
    u"Hrušč.": "USSR",
    u"LT proj.": "USSR",
    u"467.": "USSR",
    u"P. kara": "Other",
    u"119.": "USSR",
    u"M. ģim.": "USSR",
    u"Renov.": "Other",
    u"104.": "USSR",
    u"Jaun.": "New",
    u"602.": "USSR",
    u"Priv. m.": "Other",
    u"Čehu pr.": "USSR"
}

flats = Blueprint('flats', __name__)

@flats.before_request
def before_request():
    ds = bz.Data(bz.resource('mongodb://localhost/scrapy::flat'), dshape="""var * {
            open: bool,
            price: real,
            price_period: ?string,
            area: real,
            url: string,
            city: string,
            district: string,
            project: string,
            rooms: ?int
        }""")

    g.ds = ds[(ds.open == True)
        & (ds.price_period == None)]

@flats.route("/scatter-riga-area-by-price")
def scatter_riga_area_by_price():
    ds = g.ds[(g.ds.city == u'Rīga')]
    df = odo(ds, pd.DataFrame)

    return render(scatter_any(df, 'price', 'area',
        color_field='rooms',
        x_axis_type="log",
        y_axis_type="log",
        x_range=[10**3, 10**7],
        y_range=[10, 700],
        title="Price vs Area (log scale)",
        xlabel="Price",
        ylabel="Area, m2"))

@flats.route("/bar-riga-avg-price-m2-by-district")
def bar_riga_avg_price_m2_by_district():
    return _render_bar_riga_any_by_district('avg_price_m2',
        title="Price by m2 vs District",
        ylabel="m2 price (EUR)")

@flats.route("/bar-riga-avg-price-by-district")
def bar_riga_avg_price_by_district():
    return _render_bar_riga_any_by_district('avg_price',
        title="Average price vs District",
        ylabel="Price (EUR)")

@flats.route("/bar-riga-avg-area-by-district")
def bar_riga_avg_area_by_district():
    return _render_bar_riga_any_by_district('avg_area',
        title="Average area vs District",
        ylabel="Area (m2)")

@flats.route("/bar-riga-supply-by-district")
def bar_riga_supply_by_district():
    ds = g.ds[g.ds.city == u'Rīga']
    df = odo(ds, pd.DataFrame)

    df['district'] = df['district'].apply(unidecode)

    df['epoch'] = pd.Series([PROJECT_EPOCHS[x] for x in df['project']])

    # df1 = df.groupby(['district', 'epoch']).agg('size').reset_index().pivot(index='district', columns='epoch', values=0).fillna(0).reset_index()
    # df1['count'] = df1['USSR'] + df1['New'] + df1['Other']
    # df1.sort('count', ascending=False, inplace=True)

    p = Bar(df,
        label='district',
        stack='epoch',
        title="New, USSR or Other vs District",
        legend='top_right')

    return render(p)

@flats.route("/box-riga-price-mean-by-district")
def box_riga_price_mean_by_district():
    form = NoOutliersForm(request.args, csrf_enabled=False)
    outliers = not ('submit' in request.args and form.validate() and form.no_outliers.data)

    ds = g.ds[g.ds.city == u'Rīga']

    stats = _base_stats(ds)

    df = odo(ds, pd.DataFrame)

    ordered = {v: k for k, v in list(enumerate(stats.sort_values(by='avg_price_m2')['district']))}

    df['pos_mean'] = pd.Series(ordered[d] for d in df['district'])
    df['price_m2'] = df['price'] / df['area']

    df = _fix_unicode_names(df, 'district')

    df.sort(['pos_mean'], ascending=[True], inplace=True)

    p = BoxPlot(df,
        values='price_m2',
        label=cat(columns=['district'], sort=False),
        title="Price by m2 vs District (ordered by mean price of m2)",
        xlabel="District",
        ylabel="m2 price (EUR)",
        outliers=outliers
        )

    return render(p, dict(form=form))


##########################################################################################

def _render_bar_riga_any_by_district(key, **kwargs):
    ds = g.ds[(g.ds.city == u'Rīga')]

    form = FlatsNoNewProjectsForm(request.args, csrf_enabled=False)
    if 'submit' in request.args and form.validate() and form.no_new.data:
        ds = ds[ds.project != u'Jaun.']

    df = _base_stats(ds)
    df = _fix_unicode_names(df, 'district')

    df.sort([key, 'district'], ascending=[True, False], inplace=True)

    p = Bar(df,
        values=key,
        label=cat(columns=['district'], sort=False),
        xlabel="District",
        **kwargs)

    set_numerical_axis(p)

    return render(p, dict(form=form))

def _base_stats(ds):
    df = odo(bz.by(ds.district,
            sum_price=bz.sum(ds.price),
            sum_area=bz.sum(ds.area),
            count=bz.count(ds.price)),
        pd.DataFrame)

    df["avg_area"] = df["sum_area"] / df["count"]
    df["avg_price"] = df["sum_price"] / df["count"]
    df["avg_price_m2"] = df["sum_price"] / df["sum_area"]

    return df

def _fix_unicode_names(df, key):
    for index, row in df.iterrows():
        df.loc[index, key] = unidecode(row[key])

    return df
