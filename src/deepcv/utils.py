#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Utils module - utils.py - `DeepCV`__
.. moduleauthor:: Paul-Emmanuel Sotir
"""

import os
import sys
import time
import types
import random
import logging
import builtins
import threading
import importlib
import numpy as np
from pathlib import Path
from types import SimpleNamespace
from functools import singledispatch
from typing import Union, Iterable, Optional

import torch
from tqdm import tqdm
from kedro.io import DataCatalog

from src.tests.tests_utils import test_module

__all__ = ['Number', 'setup_cudnn', 'set_seeds', 'set_each_seeds', 'progess_bar',
           'get_device', 'import_and_reload', 'periodic_timer', 'cd', 'import_pickle', 'source_dir']
__author__ = 'Paul-Emmanuel Sotir'

Number = Union[builtins.int, builtins.float, builtins.bool]


def setup_cudnn(deterministic: bool = False, use_gpu: bool = torch.cuda.is_available()) -> types.ModuleType:
    if use_gpu:
        torch.backends.cudnn.deterministic = deterministic  # Makes training procedure reproducible (may have small performance impact)
        torch.backends.cudnn.benchmark = use_gpu and not torch.backends.cudnn.deterministic
        torch.backends.cudnn.fastest = use_gpu  # Disable this if memory issues
        return torch.backends.cudnn


@singledispatch
def set_seeds(all_seeds: int = 345349):
    set_each_seeds(torch_seed=all_seeds, cuda_seed=all_seeds, np_seed=all_seeds, python_seed=all_seeds)


@set_seeds.register(int)
def set_each_seeds(torch_seed: int = None, cuda_seed: int = None, np_seed: int = None, python_seed: int = None):
    if torch_seed is not None:
        torch.manual_seed(torch_seed)
    if cuda_seed is not None and torch.cuda.is_available():
        torch.cuda.manual_seed_all(cuda_seed)
    if np_seed is not None:
        np.random.seed(np_seed)
    if python_seed is not None:
        random.seed(python_seed)


def progess_bar(iterable: Iterable, desc: str, disable: bool = False):
    return tqdm(iterable, unit='batch', ncols=180, desc=desc, ascii=False, position=0, disable=disable,
                bar_format='{desc} {percentage:3.0f}%|'
                '{bar}'
                '| {n_fmt}/{total_fmt} [Elapsed={elapsed}, Remaining={remaining}, Speed={rate_fmt}{postfix}]')


def get_device() -> torch.device:
    return torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')


def start_tensorboard(port=8889, forward=False):
    raise NotImplementedError  # TODO: implementation


def stop_tensorboard(port=8889):
    raise NotImplementedError  # TODO: implementation


def import_and_reload(module_name, path='.'):
    if path not in sys.path:
        sys.path.append(path)
    module = importlib.import_module(module_name)
    module = importlib.reload(module)
    return module


class periodic_timer:
    def __init__(self, func, period=1., args=[], kwargs={}):
        self.func = func
        self.period = period
        self._args = args
        self._kwargs = kwargs

    def stop(self):
        if self._timer is not None:
            self._timer.cancel()

    def start(self, count=-1):
        if count != 0:
            start = time.time()
            self.func(*self._args, **self._kwargs)
            delta_t = time.time() - start
            self._timer = threading.Timer(max(0, self.period - delta_t), self.start, args=[count - 1])
            self._timer.start()


class cd:
    """Context manager for changing the current working directory from https://stackoverflow.com/a/13197763/5323273"""

    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def try_import(module, msg: str = 'Can\'t import module', warn: bool = True, exit_on_fail: bool = False) -> Optional[types.ModuleType]:
    import importlib
    try:
        return importlib.import_module(module)
    except ImportError as e:
        if warn:
            logging.warning(f'{msg} (module: {module})')
        if exit_on_fail:
            raise e


def import_pickle() -> types.ModuleType:
    """ Returns cPickle module if available, returns imported pickle module otherwise """
    pickle = try_import('cPickle')
    if not pickle:
        pickle = importlib.import_module('pickle')
    return pickle


def source_dir(source_file: str = __file__) -> Path:
    return Path(os.path.dirname(os.path.realpath(source_file)))


def yolo(self: DataCatalog, *search_terms):
    """you only load once, catalog loading helper"""
    return SimpleNamespace(**{
        d: self.load(d)
        for d in self.query(*search_terms)
    })


# Mokey patch catalog yolo loading :-) (code from https://waylonwalker.com/notes/kedro/)
DataCatalog.yolo = yolo
DataCatalog.yolo.__doc__ = "You Only Load Once. (Queries and loads from given search terms)"


######### TESTING #########

def test_import_and_reload():
    pathlib = import_and_reload('pathlib')
    assert pathlib is not None
    pickle = import_pickle()
    assert pickle is not None


def test_source_dir():
    path = source_dir(__file__)
    assert path.exists()
    assert path.is_file()
    assert str(path).endswith('utils.py')


if __name__ == "__main__":
    test_module(__file__)()