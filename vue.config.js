const path = require("path");

module.exports = {
  lintOnSave: false,
  outputDir: path.resolve(__dirname, "vgloss/dist"),
  configureWebpack: {
    devServer: {
      proxy: {
        "/": {
          target: "http://localhost:8000/",
        },
      }
    },
  },
}
