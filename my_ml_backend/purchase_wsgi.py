# -*- coding: utf-8 -*-
import os
import argparse
import logging
import json
import logging.config

logging.config.dictConfig({
  "version": 1,
  "formatters": {
    "standard": {
      "format": "[%(asctime)s] [%(levelname)s] [%(name)s::%(funcName)s::%(lineno)d] %(message)s"
    }
  },
  "handlers": {
    "console": {
      "class": "logging.StreamHandler",
      "level": "DEBUG",
      "stream": "ext://sys.stdout",
      "formatter": "standard"
    }
  },
  "root": {
    "level": "ERROR",
    "handlers": [
      "console"
    ],
    "propagate": True
  }
})

from label_studio.ml import init_app
from purchase_classifier import PurchaseTextClassifier


_DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')


def get_kwargs_from_config(config_path=_DEFAULT_CONFIG_PATH):
    if not os.path.exists(config_path):
        return dict()
    with open(config_path) as f:
        config = json.load(f)
    assert isinstance(config, dict)
    return config


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Label studio')
    parser.add_argument(
        '-p', '--port', dest='port', type=int, default=9090,
        help='ML的端口，默认9090')
    parser.add_argument(
        '--host', dest='host', type=str, default='0.0.0.0',
        help='ML的host地址，默认本地0.0.0.0')
    parser.add_argument(
        '--kwargs', '--with', dest='kwargs', metavar='KEY=VAL', nargs='+', type=lambda kv: kv.split('='),
        help='附加上 LabelStudioMLBase 模型的初始化参数')
    parser.add_argument(
        '-d', '--debug', dest='debug', action='store_true',
        help='是否开启debug')
    parser.add_argument(
        '--log-level', dest='log_level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default=None,
        help='日志级别')
    parser.add_argument(
        '--model-dir', dest='model_dir', default=os.path.dirname(__file__),
        help='模型的目录，例如 my_ml_backend, 相对路径，项目目录的相对路径')
    parser.add_argument(
        '--check', dest='check', action='store_true',
        help='验证模型，在启动之前')

    args = parser.parse_args()

    # setup logging level
    if args.log_level:
        logging.root.setLevel(args.log_level)

    def isfloat(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def parse_kwargs():
        param = dict()
        for k, v in args.kwargs:
            if v.isdigit():
                param[k] = int(v)
            elif v == 'True' or v == 'true':
                param[k] = True
            elif v == 'False' or v == 'False':
                param[k] = False
            elif isfloat(v):
                param[k] = float(v)
            else:
                param[k] = v
        return param

    kwargs = get_kwargs_from_config()

    if args.kwargs:
        kwargs.update(parse_kwargs())
    if args.check:
        print('Check "' + PurchaseTextClassifier.__name__ + '" instance creation..')
        model = PurchaseTextClassifier(**kwargs)

    app = init_app(
        model_class=PurchaseTextClassifier,
        model_dir=os.environ.get('MODEL_DIR', args.model_dir),
        redis_queue=os.environ.get('RQ_QUEUE_NAME', 'default'),
        redis_host=os.environ.get('REDIS_HOST', 'localhost'),
        redis_port=os.environ.get('REDIS_PORT', 6379),
        **kwargs
    )

    app.run(host=args.host, port=args.port, debug=args.debug)

else:
    # for uWSGI use
    print("注意：使用的默认的模型")
    app = init_app(
        model_class=PurchaseTextClassifier,
        model_dir=os.environ.get('MODEL_DIR', os.path.dirname(__file__)),
        redis_queue=os.environ.get('RQ_QUEUE_NAME', 'default'),
        redis_host=os.environ.get('REDIS_HOST', 'localhost'),
        redis_port=os.environ.get('REDIS_PORT', 6379)
    )
