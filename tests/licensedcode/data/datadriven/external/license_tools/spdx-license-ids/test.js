'use strict';

const deprecated = require('./deprecated');
const valid = require('.');
const test = require('tape');

(async () => {
	await require('./build.js');

	test('require(\'spdx-license-ids\')', t => {
		t.ok(Array.isArray(valid), 'should be an array.');

		t.ok(
			valid.includes('LGPL-3.0-or-later'),
			'should include non-deprecated license IDs.'
		);

		t.notOk(
			valid.includes('Nunit'),
			'should not include deprecated license IDs.'
		);

		t.end();
	});

	test('require(\'spdx-license-ids/deprecated\')', t => {
		t.ok(Array.isArray(deprecated), 'should be an array.');

		t.ok(
			deprecated.length < valid.length,
			'should be smaller than the main export.'
		);

		t.ok(
			deprecated.includes('eCos-2.0'),
			'should include deprecated license IDs.'
		);

		t.notOk(
			deprecated.includes('ISC'),
			'should not include non-deprecated license IDs.'
		);

		t.end();
	});
})();
