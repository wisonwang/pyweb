# -*- coding: utf-8 -*-
"""
如果通过swagger（connexion）构建一个api first服务。

"""

from connexion import app
import os


class ApiApplication(app.App):
    def __init__(self, *args, **kw):
        """
        :param import_name: the name of the application package
        :type import_name: str
        :param host: the host interface to bind on.
        :type host: str
        :param port: port to listen to
        :type port: int
        :param specification_dir: directory where to look for specifications
        :type specification_dir: pathlib.Path | str
        :param server: which wsgi server to use, tornado or gevent
        :type server: str | None
        :param arguments: arguments to replace on the specification
        :type arguments: dict | None
        :param auth_all_paths: whether to authenticate not defined paths
        :type auth_all_paths: bool
        :param debug: include debugging information
        :type debug: bool
        :param swagger_json: whether to include swagger json or not
        :type swagger_json: bool
        :param swagger_ui: whether to include swagger ui or not
        :type swagger_ui: bool
        :param swagger_path: path to swagger-ui directory
        :type swagger_path: string | None
        :param swagger_url: URL to access swagger-ui documentation
        :type swagger_url: string | None
        :param validator_map: map of validators
        :type validator_map: dict
        """
        app.App.__init__(self, *args, **kw)


def run_server(
        port=8000,
        package=__name__,
        specification_base_dir="swagger/",
        ip="0.0.0.0",
        arguments={"appName": "test"},
        *arg, **kw):
    """
    
    """
    app = ApiApplication(package,
                         specification_dir=specification_base_dir,
                         arguments=arguments,
                         *arg, **kw)
    
    add_api = lambda yaml_file: app.add_api(
        yaml_file, arguments=arguments)
        
    for root, dirs, files in os.walk(specification_base_dir):
        for i in files:
            if os.path.splitext(i)[1] == ".yaml":
                print i, root
                if root == specification_base_dir:
                    add_api(i)
                else:
                    path = os.path.join(root[len(specification_base_dir):], i)
                    add_api(path)
    app.run(port=port)
