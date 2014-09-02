# -*- coding: utf-8 -*-
# Copyright (c) 2014 Polytechnique.org
# This software is distributed under the GPLv3+ license.


import logging


class ProcessError(Exception):
    """Base exception for all process-related errors."""


class operation(object):
    def __init__(self, checker):
        self.checker = checker

    def __call__(self, target):
        return OperationWrapper(self.checker, target)


class OperationWrapper(object):
    def __init__(self, checker, target):
        self.checker = checker
        self.target = target

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return InstanceOperationWrapper(
            instance=instance,
            checker=self.checker,
            target=self.target,
        )


class InstanceOperationWrapper(object):
    def __init__(self, instance, checker, target):
        self.checker = checker
        self.target = target
        self.instance = instance

    def is_available(self):
        return self.checker(self.instance)

    def __call__(self, *args, **kwargs):
        if not self.is_available():
            raise ProcessError()
        logger = logging.getLogger(self.instance.__class__.__module__)

        try:
            result = self.target(self.instance, *args, **kwargs)
        except Exception as e:
            logger.exception("Call to %r.%s(*%r, **%r) raised %s",
                self.instance, self.target.__name__, args, kwargs, e)
            raise
        else:
            logger.info("Call to %r.%s(*%r, **%r) returned %r",
                self.instance, self.target.__name__, args, kwargs, result)
            return result


