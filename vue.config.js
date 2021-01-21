const path = require("path");
const ESLintPlugin = require('eslint-webpack-plugin');

let djangoDevUrl = "http://localhost:8000/";

// Double django-webpack templating
//
// The html for our single-page app, public/vue-single-page.html, is a template
// file for both HtmlWebpackPlugin and Django.
//
// Webpack reads the template `public/vue-single-page.html` and writes output
// to `vgloss/templates/vgloss/vue-single-page.html`. It injects the JS/CSS
// assets needed at this step. This happens even when running the webpack dev
// server.
//
// The double-templating loosely follows this guide:
//   https://github.com/EugeneDae/django-vue-cli-webpack-demo

module.exports = {
  lintOnSave: false,
  outputDir: path.resolve(__dirname, "vgloss/dist"),

  configureWebpack: {
    devServer: {
      proxy: {
        // Use negative lookahead to match any URL not starting with a path
        // explicitly known to be handled by webpack. E.g. proxy any URL not
        // starting with /js/, /css/, etc.
        "^((?!\\/js\\/|\\/css\\/|\\/img\\/|\\/sockjs-node\\/).)+.*$": {
          target: djangoDevUrl,
         },
      },
    },

    plugins: [new ESLintPlugin({
      files: "src/",
      extensions: ["js", "vue"],
    })],
  },

  chainWebpack: config => {
    // Always write vue-single-page template to disk, since Django will read
    // from it.
    config.devServer
      .public("http://localhost:8001/")
      .hotOnly(true)
      .headers({"Access-Control-Allow-Origin": "*"})
      .writeToDisk(filePath => filePath.endsWith('vue-single-page.html'));

    // Configure HtmlWebpackPlugin to read from our vue-single-page template
    // and write it into the django templates folder.
    // Vue-cli sets this plugin up automatically, but we're modifying it's
    // config here. Note that we can't name this file "index.html", since it
    // vue-cli's proxy has a special case to always serve files which exist in
    // public/. See:
    //   https://github.com/vuejs/vue-cli/blob/4378c8df26a007abe1a023ab2f61cadd6d0eec3d/packages/%40vue/cli-service/lib/util/prepareProxy.js#L50
    config.plugin("html").tap(htmlConf => {
      htmlConf[0].template = "public/vue-single-page.html";
      htmlConf[0].filename = "../templates/vgloss/vue-single-page.html";
      return htmlConf;
    });
  },

}
