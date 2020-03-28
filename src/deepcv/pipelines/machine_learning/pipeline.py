#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Example code for the nodes in the example pipeline. This code is meant
just for illustrating basic Kedro features.

Delete this when you start working on your own Kedro project.
"""

from kedro.pipeline import Pipeline, node

from .nodes import predict, report_accuracy, train_model

__author__ = 'Paul-Emmanuel Sotir'


def create_pipeline(**kwargs):
    return Pipeline(
        [node(train_model, ["example_train_x", "example_train_y", "parameters"], "example_model"),
         node(predict, {'model': "example_model", 'test_x': "example_test_x"}, "example_predictions"),
         node(report_accuracy, ["example_predictions", "example_test_y"], None)],
        name='training_pipeline')