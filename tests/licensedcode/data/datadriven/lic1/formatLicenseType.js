/**
* @file format license types
*/

const colors = require('colors/safe');

const labels = {
  publicDomain: `Public Domain`,
  permissive: `Permissive`,
  weaklyProtective: `Weakly Protective`,
  protective: `Protective`,
  networkProtective: `Network Protective`,
  uncategorized: `Uncategorized`
};

const palette = {
  publicDomain: `green`,
  permissive: `green`,
  weaklyProtective: `cyan`,
  protective: `magenta`,
  networkProtective: `magenta`,
  uncategorized: `grey`
};

module.exports = function formatLicenseType(type) {
  return colors[palette[type]](labels[type]);
};
