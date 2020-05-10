const path = require("path");

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
      },
    },
  },
}
