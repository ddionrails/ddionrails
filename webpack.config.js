/*!
 * ddionrails - webpack configuration
 * Copyright 2018-2019
 * Licensed under AGPL (https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md)
 */

var path = require("path");
var webpack = require("webpack");
var BundleTracker = require("webpack-bundle-tracker");
var ExtractTextPlugin = require("extract-text-webpack-plugin");
var glob = require("glob");

entry: glob.sync("./test/**/*Spec.js");

module.exports = {
  context: __dirname,
  entry: {
    /* css and js libraries for ddionrails */
    index: "./assets/js/index.js",
    topics: ["./assets/js/topics.js", "./assets/scss/topics.scss"],
    visualization: ["./assets/js/visualization.js", "./assets/scss/visualization.scss"],

    /* Workaround:
       ddionrails-elasticsearch: search library
    */
    elasticsearch_inline: glob.sync(
      "./node_modules/ddionrails-elasticsearch/dist/inline.*.bundle.js"
    ),
    elasticsearch_polyfills: glob.sync(
      "./node_modules/ddionrails-elasticsearch/dist/polyfills.*.bundle.js"
    ),
    elasticsearch_vendor: glob.sync(
      "./node_modules/ddionrails-elasticsearch/dist/vendor.*.bundle.js"
    ),
    elasticsearch_main: glob.sync(
      "./node_modules/ddionrails-elasticsearch/dist/main.*.bundle.js"
    )
  },
  output: {
    path: path.resolve("./static/dist/"),
    filename: "[name]-[hash].js"
  },

  plugins: [
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery"
    }),
    new BundleTracker({ filename: "./webpack-stats.json" }),
    new ExtractTextPlugin({ filename: "[name]-[hash].css" })
  ],

  module: {
    rules: [
      {
        test: /\.scss$/,
        use: ExtractTextPlugin.extract({
          fallback: "style-loader",
          use: ["css-loader", "sass-loader"]
        })
      },
      /* Loads fonts, used for Bootstrap */
      {
        test: /\.(woff(2)?|ttf|eot|svg)$/,
        use: [
          {
            loader: "file-loader",
            options: {
              name: "[name].[ext]",
              outputPath: "fonts/"
            }
          }
        ]
      },
      {
        test: /\.(png|jpg|gif)$/,
        use: [
          {
            loader: "file-loader",
            options: {}
          }
        ]
      }
    ]
  },
  resolve: {
    extensions: [".js", ".jsx"],
    modules: [path.resolve(__dirname, "node_modules")]
  }
};
