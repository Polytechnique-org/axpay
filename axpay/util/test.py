# -*- coding: utf-8 -*-
# Copyright (c) 2014 Polytechnique.org
# This software is distributed under the GPLv3+ license.


from django.conf import settings
from django.test.simple import DjangoTestSuiteRunner

import xmlrunner


class BalTestSuiteRunner(DjangoTestSuiteRunner):
    def build_suite(self, test_labels, extra_tests=None, **kwargs):

        # Test only the applications in TEST_APPS
        if not test_labels and settings.TEST_APPS:
            test_labels = [app.split('.')[-1] for app in settings.TEST_APPS]

        # Add regular tests if required
        return super().build_suite(test_labels, **kwargs)


class BalXMLTestSuiteRunner(BalTestSuiteRunner):
    def run_suite(self, suite, **kwargs):
        """Run the suite and generate an XML report."""
        options = {
            'verbosity': getattr(settings, 'TEST_OUTPUT_VERBOSE', False),
            'descriptions': getattr(settings, 'TEST_OUTPUT_DESCRIPTIONS', False),
            'output': getattr(settings, 'TEST_OUTPUT_DIR', '.'),
            'outsuffix': 'result',  # No date-based file suffix
        }
        return xmlrunner.XMLTestRunner(**options).run(suite)
