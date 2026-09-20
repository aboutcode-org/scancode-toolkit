#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
from packagedcode import models
from commoncode.testcase import FileBasedTesting
from packages_test_utils import compare_package_results
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES
from packagedcode import componentjs

class TestComponentJSON(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_scanworks_on_component_jszip(self):
        test_file = self.get_test_loc('componentjs/jszip/component.json')
        expected_file = self.get_test_loc('componentjs/jszip/expectedoutput.json')
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_file, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES)

    def test_scanworks_on_component_knockback(self):
        test_file = self.get_test_loc('componentjs/knockback/component.json')
        expected_file = self.get_test_loc('componentjs/knockback/expectedoutput.json')
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_file, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES)

    def test_scanworks_on_component_angular_ui_sortable(self):
        test_file = self.get_test_loc('componentjs/angular-ui-sortable/component.json')
        expected_file = self.get_test_loc('componentjs/angular-ui-sortable/expectedoutput.json')
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_file, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES)

    def test_scanworks_on_component_seedrandom(self):
        test_file = self.get_test_loc('componentjs/seedrandom/component.json')
        expected_file = self.get_test_loc('componentjs/seedrandom/expectedoutput.json')
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_file, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES)

    def test_scanworks_on_component_chai(self):
        test_file = self.get_test_loc('componentjs/chai/component.json')
        expected_file = self.get_test_loc('componentjs/chai/expectedoutput.json')
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_file, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES)

    def test_parse_jszip_component_json(self):
        test_file = self.get_test_loc('componentjs/jszip/component.json')
        result_packages = list(componentjs.ComponentJSONMetadataHandler.parse(test_file))
        expected_packages = [
            models.PackageData(
                type=componentjs.ComponentJSONMetadataHandler.default_package_type,
                datasource_id=componentjs.ComponentJSONMetadataHandler.datasource_id,
                declared_license_expression= "mit OR gpl-3.0",
                declared_license_expression_spdx= "MIT OR GPL-3.0-only",
                name="jszip",
                namespace="Stuk",
                version="3.2.0",
                description="Create, read and edit .zip files with JavaScript http://stuartk.com/jszip",
                homepage_url="https://github.com/Stuk/jszip",
                keywords=["zip", "deflate", "inflate"],
                extracted_license_statement="type: MIT or GPLv3",
                license_detections= [
                    {
                    "license_expression": "mit OR gpl-3.0",
                    "license_expression_spdx": "MIT OR GPL-3.0-only",
                    "matches": [
                        {
                        "license_expression": "mit OR gpl-3.0",
                        "license_expression_spdx": "MIT OR GPL-3.0-only",
                        "from_file": None,
                        "start_line": 1,
                        "end_line": 1,
                        "matcher": "2-aho",
                        "score": 100.0,
                        "matched_length": 3,
                        "match_coverage": 100.0,
                        "rule_relevance": 100,
                        "rule_identifier": "mit_or_gpl-3.0_1.RULE",
                        "rule_url": "https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/rules/mit_or_gpl-3.0_1.RULE",
                        "matched_text": "type: MIT or GPLv3"
                        }
                    ],
                    "identifier": "mit_or_gpl_3_0-9dbb60be-81c9-331c-96a6-8e6723aa5ce9"
                    }
                ],
                extra_data={
                    "main": "dist/jszip.js",
                    "scripts": ["dist/jszip.js"]
                }
            )
        ]
        compare_package_results(expected_packages, result_packages)

    def test_parse_knockback_component_json(self):
        test_file = self.get_test_loc('componentjs/knockback/component.json')
        result_packages = list(componentjs.ComponentJSONMetadataHandler.parse(test_file))
        expected_packages = [
            models.PackageData(
                type=componentjs.ComponentJSONMetadataHandler.default_package_type,
                datasource_id=componentjs.ComponentJSONMetadataHandler.datasource_id,
                declared_license_expression= "mit",
                declared_license_expression_spdx= "MIT",
                name="knockback",
                namespace="kmalakoff",
                version="1.2.3",
                description="Knockback.js provides Knockout.js magic for Backbone.js Models and Collections",
                homepage_url="https://github.com/kmalakoff/knockback",
                keywords=["knockback", "knockbackjs", "backbone", "backbonejs", "knockout", "knockoutjs"],
                extracted_license_statement="type: MIT",
                license_detections= [
                    {
                    "license_expression": "mit",
                    "license_expression_spdx": "MIT",
                    "matches": [
                        {
                        "license_expression": "mit",
                        "license_expression_spdx": "MIT",
                        "from_file": None,
                        "start_line": 1,
                        "end_line": 1,
                        "matcher": "1-hash",
                        "score": 16.0,
                        "matched_length": 3,
                        "match_coverage": 100.0,
                        "rule_relevance": 16,
                        "rule_identifier": "mit_1301.RULE",
                        "rule_url": "https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/rules/mit_1301.RULE",
                        "matched_text": "license type: MIT"
                        }
                    ],
                    "identifier": "mit-1c9cba21-81d2-7522-ac3e-dfde6630f8d1"
                    }
                ],
                dependencies=[
                    models.DependentPackage(
                        purl="pkg:generic/jashkenas/underscore@%2A",
                        scope="runtime",
                        is_runtime=True,
                        is_optional=False
                    ),
                    models.DependentPackage(
                        purl="pkg:generic/jashkenas/backbone@%2A",
                        scope="runtime",
                        is_runtime=True,
                        is_optional=False
                    ),
                    models.DependentPackage(
                        purl="pkg:generic/kmalakoff/knockout@%2A",
                        scope="runtime",
                        is_runtime=True,
                        is_optional=False
                    )
                ],
                extra_data={
                    "main": "knockback.js",
                    "scripts": ["knockback.js"]
                }
            )
        ]
        compare_package_results(expected_packages, result_packages)

    def test_parse_angular_ui_sortable_component_json(self):
        test_file = self.get_test_loc('componentjs/angular-ui-sortable/component.json')
        result_packages = list(componentjs.ComponentJSONMetadataHandler.parse(test_file))
        expected_packages = [
            models.PackageData(
                type=componentjs.ComponentJSONMetadataHandler.default_package_type,
                datasource_id=componentjs.ComponentJSONMetadataHandler.datasource_id,
                declared_license_expression= "mit",
                declared_license_expression_spdx= "MIT",
                name="angular-ui-sortable",
                version="0.0.1",
                description="This directive allows you to jQueryUI Sortable.",
                homepage_url="http://angular-ui.github.com",
                dependencies=[
                    models.DependentPackage(
                        purl="pkg:generic/angular@~1.x",
                        scope="runtime",
                        is_runtime=True,
                        is_optional=False
                    ),
                    models.DependentPackage(
                        purl="pkg:generic/jquery-ui@%3E%3D%201.9",
                        scope="runtime",
                        is_runtime=True,
                        is_optional=False
                    )
                ],
                extracted_license_statement="type: MIT",
                license_detections= [
                    {
                    "license_expression": "mit",
                    "license_expression_spdx": "MIT",
                    "matches": [
                        {
                        "license_expression": "mit",
                        "license_expression_spdx": "MIT",
                        "from_file": None,
                        "start_line": 1,
                        "end_line": 1,
                        "matcher": "1-hash",
                        "score": 16.0,
                        "matched_length": 3,
                        "match_coverage": 100.0,
                        "rule_relevance": 16,
                        "rule_identifier": "mit_1301.RULE",
                        "rule_url": "https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/rules/mit_1301.RULE",
                        "matched_text": "license type: MIT"
                        }
                    ],
                    "identifier": "mit-1c9cba21-81d2-7522-ac3e-dfde6630f8d1"
                    }
                ],
                extra_data={
                    "main": "./src/sortable.js"
                }
            )
        ]
        compare_package_results(expected_packages, result_packages)

    def test_parse_seedrandom_component_json(self):
        test_file = self.get_test_loc('componentjs/seedrandom/component.json')
        result_packages = list(componentjs.ComponentJSONMetadataHandler.parse(test_file))
        expected_packages = [
            models.PackageData(
                type=componentjs.ComponentJSONMetadataHandler.default_package_type,
                datasource_id=componentjs.ComponentJSONMetadataHandler.datasource_id,
                declared_license_expression= "mit",
                declared_license_expression_spdx= "MIT",
                name="seedrandom",
                version="2.3.10",
                description="Seeded random number generator for Javascript",
                homepage_url=None,
                keywords=["random", "seed", "crypto"],
                license_detections= [
                    {
                    "license_expression": "mit",
                    "license_expression_spdx": "MIT",
                    "matches": [
                        {
                        "license_expression": "mit",
                        "license_expression_spdx": "MIT",
                        "from_file": None,
                        "start_line": 1,
                        "end_line": 1,
                        "matcher": "1-hash",
                        "score": 16.0,
                        "matched_length": 3,
                        "match_coverage": 100.0,
                        "rule_relevance": 16,
                        "rule_identifier": "mit_1301.RULE",
                        "rule_url": "https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/rules/mit_1301.RULE",
                        "matched_text": "license type: MIT"
                        }
                    ],
                    "identifier": "mit-1c9cba21-81d2-7522-ac3e-dfde6630f8d1"
                    }
                ],
                extracted_license_statement="type: MIT",
                extra_data={
                    "main": "seedrandom.js",
                    "scripts": ["seedrandom.js"],
                    "repository": "davidbau/seedrandom"
                }
            )
        ]
        compare_package_results(expected_packages, result_packages)

    def test_parse_chai_component_json(self):
        test_file = self.get_test_loc('componentjs/chai/component.json')
        result_packages = list(componentjs.ComponentJSONMetadataHandler.parse(test_file))
        expected_packages = [
            models.PackageData(
                type=componentjs.ComponentJSONMetadataHandler.default_package_type,
                datasource_id=componentjs.ComponentJSONMetadataHandler.datasource_id,
                declared_license_expression= "mit",
                declared_license_expression_spdx= "MIT",
                name="chai",
                namespace="chaijs",
                version="2.1.2",
                description="BDD/TDD assertion library for node.js and the browser. Test framework agnostic.",
                homepage_url="https://github.com/chaijs/chai",
                keywords=["test", "assertion", "assert", "testing", "chai"],
                dependencies=[
                    models.DependentPackage(
                        purl="pkg:generic/chaijs/assertion-error@1.0.0",
                        scope="runtime",
                        is_runtime=True,
                        is_optional=False
                    ),
                    models.DependentPackage(
                        purl="pkg:generic/chaijs/deep-eql@0.1.3",
                        scope="runtime",
                        is_runtime=True,
                        is_optional=False
                    )
                ],
                extracted_license_statement="type: MIT",
                license_detections= [
                    {
                    "license_expression": "mit",
                    "license_expression_spdx": "MIT",
                    "matches": [
                        {
                        "license_expression": "mit",
                        "license_expression_spdx": "MIT",
                        "from_file": None,
                        "start_line": 1,
                        "end_line": 1,
                        "matcher": "1-hash",
                        "score": 16.0,
                        "matched_length": 3,
                        "match_coverage": 100.0,
                        "rule_relevance": 16,
                        "rule_identifier": "mit_1301.RULE",
                        "rule_url": "https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/rules/mit_1301.RULE",
                        "matched_text": "license type: MIT"
                        }
                    ],
                    "identifier": "mit-1c9cba21-81d2-7522-ac3e-dfde6630f8d1"
                    }
                ],
                extra_data={
                    "main": "index.js",
                    "scripts": [
                        "index.js",
                        "lib/chai.js",
                        "lib/chai/assertion.js",
                        "lib/chai/config.js",
                        "lib/chai/core/assertions.js",
                        "lib/chai/interface/assert.js",
                        "lib/chai/interface/expect.js",
                        "lib/chai/interface/should.js",
                        "lib/chai/utils/addChainableMethod.js",
                        "lib/chai/utils/addMethod.js",
                        "lib/chai/utils/addProperty.js",
                        "lib/chai/utils/flag.js",
                        "lib/chai/utils/getActual.js",
                        "lib/chai/utils/getEnumerableProperties.js",
                        "lib/chai/utils/getMessage.js",
                        "lib/chai/utils/getName.js",
                        "lib/chai/utils/getPathValue.js",
                        "lib/chai/utils/getPathInfo.js",
                        "lib/chai/utils/hasProperty.js",
                        "lib/chai/utils/getProperties.js",
                        "lib/chai/utils/index.js",
                        "lib/chai/utils/inspect.js",
                        "lib/chai/utils/objDisplay.js",
                        "lib/chai/utils/overwriteMethod.js",
                        "lib/chai/utils/overwriteProperty.js",
                        "lib/chai/utils/overwriteChainableMethod.js",
                        "lib/chai/utils/test.js",
                        "lib/chai/utils/transferFlags.js",
                        "lib/chai/utils/type.js"
                    ],
                    "development": {}
                }
            )
        ]
        compare_package_results(expected_packages, result_packages)