module.exports = {
  extends: [
    'airbnb',
    'prettier',
    'prettier/flowtype',
    'prettier/react',
    'plugin:flowtype/recommended',
  ],
  parser: 'babel-eslint',
  plugins: ['prettier', 'flowtype', 'react-functional-set-state'],
  env: {
    browser: true,
    node: true,
    jest: true,
  },
  rules: {
    'no-undef-init': 1,
    'react/sort-comp': [
      1,
      {
        order: [
          'type-annotations',
          'static-methods',
          'lifecycle',
          'everything-else',
          'render',
        ],
        groups: {
          rendering: ['/^render.+$/', 'render'],
        },
      },
    ],
    'react/jsx-filename-extension': [
      1,
      {
        extensions: ['.js'],
      },
    ],
    'react-functional-set-state/no-this-state-props': 2,
    'import/no-extraneous-dependencies': [
      'error',
      {
        devDependencies: true,
      },
    ],
    'prettier/prettier': [
      'error',
      {
        trailingComma: 'all',
        singleQuote: true,
      },
    ],
  },
};
