module.exports = {
  root: true,
  parser: 'babel-eslint',
  env: {
    browser: true,
    node: true,
    jquery: true
  },
  extends: 'standard',
  // required to lint *.vue files
  plugins: [
    'html',
    'vue'
  ],
  // add your custom rules here
  rules: {},
  globals: {
    "RobustWebSocket": "readable"
  }
}
