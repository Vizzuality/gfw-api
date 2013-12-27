# Global Forest Watch API
# Copyright (C) 2013 World Resource Institute
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""This module supports accessing hansen data."""

import json
import ee
import logging
import config


def _get_coords(geojson):
    return geojson.get('coordinates')


def _loss(params):
    ee.Initialize(config.EE_CREDENTIALS, config.EE_URL)
    loss_by_year = ee.Image(config.assets['hansen_loss'])
    poly = _get_coords(json.loads(params.get('geom')))
    params.pop('geom')
    params.pop('layer')
    if params.get('maxPixels'):
        params['maxPixels'] = int(params['maxPixels'])
    if params.get('tileScale'):
        params['tileScale'] = int(params['tileScale'])
    if params.get('scale'):
        params['scale'] = int(params['scale'])
    else:
        params['scale'] = 90
    if params.get('bestEffort'):
        params['bestEffort'] = bool(params['bestEffort'])
    else:
        params['bestEffort'] = True
    region = ee.Geometry.Polygon(poly)
    reduce_args = {
        'reducer': ee.Reducer.sum(),
        'geometry': region
    }
    reduce_args.update(params)
    area_stats = loss_by_year.divide(1000 * 1000 * 255.0) \
        .multiply(ee.Image.pixelArea()) \
        .reduceRegion(**reduce_args)
    area_results = area_stats.getInfo()
    area = ee.Image.pixelArea().reduceRegion(**reduce_args).get('area')
    percent_stats = loss_by_year.multiply(100.0 / 255.0) \
        .divide(ee.Image.constant(area)) \
        .multiply(ee.Image.pixelArea()) \
        .reduceRegion(**reduce_args)
    percent_results = percent_stats.getInfo()
    logging.info(area_results)
    logging.info(percent_results)
    return dict(area=area_results, percent=percent_results)


def download(params):
    pass


def analyze(params):
    layer = params.get('layer')
    if layer == 'loss':
        return _loss(params)