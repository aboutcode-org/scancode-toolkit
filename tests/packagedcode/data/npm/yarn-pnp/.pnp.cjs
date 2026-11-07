// DRAFT test fixture — v2, real Yarn Berry shape (see CORRECTION.md).
// packageRegistryData is a LIST of [ident, [[reference, data], ...]] pairs.
// References are locators ("npm:7.0.0"), not plain versions. The first entry
// The first entry, with null ident and null reference, is the top-level workspace root itself.
// The two npm entries below intentionally reproduce the v1 fixture's packages,
// so the expected output (.pnp.cjs-expected) is unchanged: @babel/core 7.0.0
// and lodash 4.17.21 — only the input shape is corrected.
const RAW_RUNTIME_STATE = {"packageRegistryData": [[null, [[null, {"packageLocation": "./", "packageDependencies": [["@babel/core", "npm:7.0.0"], ["lodash", "npm:4.17.21"]], "linkType": "SOFT"}]]], ["@babel/core", [["npm:7.0.0", {"packageLocation": "./.yarn/cache/@babel-core-npm-7.0.0-abc.zip/node_modules/@babel/core/", "packageDependencies": [], "linkType": "HARD"}]]], ["lodash", [["npm:4.17.21", {"packageLocation": "./.yarn/cache/lodash-npm-4.17.21-def.zip/node_modules/lodash/", "packageDependencies": [], "linkType": "HARD"}]]]]};
