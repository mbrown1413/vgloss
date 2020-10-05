const path = require("path");
const ESLintPlugin = require('eslint-webpack-plugin');

module.exports = {
  lintOnSave: false,
  outputDir: path.resolve(__dirname, "vgloss/dist"),
  configureWebpack: {
    devServer: {
      proxy: {
        "^/api/": {
          target: "http://localhost:8000/",
        },
        "^/file/": {
          target: "http://localhost:8000/",
        },
        "^/static/": {  // DRF's static files
          target: "http://localhost:8000/",
        },
      },
    },
    plugins: [new ESLintPlugin({
      files: "src/",
      extensions: ["js", "vue"],
    })],
  },
}
