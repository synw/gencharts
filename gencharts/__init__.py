# -*- coding: utf-8 -*-

import os
import json
import pandas as pd
from altair import Chart, X, Y, Axis, Scale, Size, Data, Color, Shape
from goerr import err


class ChartsGenerator():

    def gen(self, slug, name, dataobj, xfield, yfield, time_unit=None,
            chart_type="line", width=800,
            height=300, color=Color(), size=Size(),
            scale=Scale(zero=False), shape=Shape(), filepath=None,
            html_before="", html_after=""):
        """
        Generates an html chart from either a pandas dataframe, a dictionnary,
        a list or an Altair Data object and optionally write it to a file
        """
        chart_obj = self.serialize(dataobj, xfield, yfield, time_unit,
                                   chart_type, width, height, color, size, scale, shape)
        html = self.html(slug, name, chart_obj, filepath,
                         html_before, html_after)
        return html

    def html(self, slug, name, chart_obj, filepath=None,
             html_before="", html_after=""):
        """
        Generate html from an Altair chart object and optionally write it to a file
        """
        try:
            html = ""
            if name:
                html = "<h3>" + name + "</h3>"
            json_data = chart_obj.to_json()
            json_data = self._patch_json(json_data)
            html = html_before + html +\
                self._json_to_html(slug, json_data) + html_after
        except Exception as e:
            err.new(e)
        # generate file
        if filepath is not None:
            self._write_file(slug, filepath, html)
            return None
        else:
            return html

    def serialize(self, dataobj, xfield, yfield, time_unit=None,
                  chart_type="line", width=800,
                  height=300, color=None, size=None,
                  scale=Scale(zero=False), shape=None, options={}):
        """
        Serialize to an Altair chart object from either a pandas dataframe, a dictionnary,
        a list or an Altair Data object
        """
        dataset = dataobj
        if self._is_dict(dataobj) is True:
            dataset = self._dict_to_df(dataobj, xfield, yfield)
        elif isinstance(dataobj, list):
            dataset = Data(values=dataobj)
        xencode, yencode = self._encode_fields(
            xfield, yfield, time_unit)
        opts = dict(x=xencode, y=yencode)
        if color is not None:
            opts["color"] = color
        if size is not None:
            opts["size"] = size
        if shape is not None:
            opts["shape"] = shape
        chart = self._chart_class(dataset, chart_type, **options).encode(
            **opts
        ).configure_cell(
            width=width,
            height=height,
        )
        return chart

    def serialize_date(self, date):
        """
        Serializes a datetime object to Vega Lite format
        """
        return date.strftime("%Y-%m-%d %H:%M:%S")

    def _patch_json(self, json_data):
        """
        Patch the Altair generated json to the newest Vega Lite spec
        """
        json_data = json.loads(json_data)
        # add schema
        json_data["$schema"] = "https://vega.github.io/schema/vega-lite/2.0.0-beta.15.json"
        # add top level width and height
        json_data["width"] = json_data["config"]["cell"]["width"]
        json_data["height"] = json_data["config"]["cell"]["height"]
        del(json_data["config"]["cell"])
        return json.dumps(json_data)

    def _json_to_html(self, slug, json_data):
        """
        Generates html from Vega lite data
        """
        html = '<div id="chart-' + slug + '"></div>'
        html += '<script>'
        html += 'var s' + slug + ' = ' + json_data + ';'
        html += 'vega.embed("#chart-' + slug + '", s' + slug + ');'
        #html += 'console.log(JSON.stringify(s{id}, null, 2));'
        html += '</script>'
        return html

    def _dict_to_df(self, dictobj, xfield, yfield):
        """
        Converts a dictionnary to a pandas dataframe
        """
        x = []
        y = []
        for datapoint in dictobj:
            x.append(datapoint)
            y.append(dictobj[datapoint])
        df = pd.DataFrame({xfield[0]: x, yfield[0]: y})
        return df

    def _is_dict(self, dataobj):
        """
        Check if the data object is a dictionnary
        """
        if isinstance(dataobj, dict):
            return True
        return False

    def _write_file(self, slug, folderpath, html):
        """
        Writes a chart's html to a file
        """
        # check directories

        if not os.path.isdir(folderpath):
            try:
                os.makedirs(folderpath)
            except Exception as e:
                err.new(e)
        # construct file path
        filepath = folderpath + "/" + slug + ".html"
        #~ write the file
        try:
            filex = open(filepath, "w")
            filex.write(html)
            filex.close()
        except Exception as e:
            err.new(e)

    def _chart_class(self, df, chart_type, **kwargs):
        """
        Get the right chart class from a string
        """
        if chart_type == "bar":
            return Chart(df).mark_bar(**kwargs)
        elif chart_type == "circle":
            return Chart(df).mark_circle(**kwargs)
        elif chart_type == "line":
            return Chart(df).mark_line(**kwargs)
        elif chart_type == "point":
            return Chart(df).mark_point(**kwargs)
        elif chart_type == "area":
            return Chart(df).mark_area(**kwargs)
        elif chart_type == "tick":
            return Chart(df).mark_tick(**kwargs)
        elif chart_type == "text":
            return Chart(df).mark_text(**kwargs)
        elif chart_type == "square":
            return Chart(df).mark_square(**kwargs)
        elif chart_type == "rule":
            return Chart(df).mark_rule(**kwargs)
        return None

    def _encode_fields(self, xfield, yfield, time_unit=None, scale=Scale(zero=False)):
        """
        Encode the fields in Altair format
        """
        if scale is None:
            scale = Scale()
        xfieldtype = xfield[1]
        yfieldtype = yfield[1]
        x_options = None
        if len(xfield) > 2:
            x_options = xfield[2]
        y_options = None
        if len(yfield) > 2:
            y_options = yfield[2]
        if time_unit is not None:
            if x_options is None:
                xencode = X(xfieldtype, timeUnit=time_unit)
            else:
                xencode = X(
                    xfieldtype,
                    axis=Axis(**x_options),
                    timeUnit=time_unit,
                    scale=scale
                )
        else:
            if x_options is None:
                xencode = X(xfieldtype)
            else:
                xencode = X(
                    xfieldtype,
                    axis=Axis(**x_options),
                    scale=scale
                )
        if y_options is None:
            yencode = Y(yfieldtype, scale=scale)
        else:
            yencode = Y(
                yfieldtype,
                axis=Axis(**y_options),
                scale=scale
            )
        return xencode, yencode
