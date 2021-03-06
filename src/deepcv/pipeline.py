#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Construction of the master pipeline.
"""
from typing import Dict

from kedro.pipeline import Pipeline
import kedro.pipeline.decorators as dec

from .detection.object import get_object_detector_pipelines

DECORATORS = [dec.log_time, dec.mem_profile]  # Other decorator available: retry, spark_to_pandas, pandas_to_spark

__author__ = 'Paul-Emmanuel Sotir'


def create_pipelines(**kwargs) -> Dict[str, Pipeline]:
    """Create the project's pipeline.
    Args:
        kwargs: Ignore any additional arguments added in the future.
    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.
    """
    pipeline_mapping = {}
    pipeline_mapping.update({p.name: p.decorate(*DECORATORS) for p in get_object_detector_pipelines()})
    return {**pipeline_mapping, "__default__": sum([p for n, p in pipeline_mapping])}
