/*!
 * ddionrails - webpack configuration
 * Copyright 2018-2019
 * Licensed under AGPL (https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md)
 */

const path = require("path");
const webpack = require("webpack");
const BundleTracker = require("webpack-bundle-tracker");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const glob = require("glob");

entry: glob.sync("./test/**/*Spec.js");

module.exports = {
  context: __dirname,
  entry: {
    /* css and js libraries for ddionrails */
    index: "./assets/js/index.js",
    topics: ["./assets/js/topics.js", "./assets/scss/topics.scss"],
    visualization: [
      "./assets/js/visualization.js",
      "./assets/scss/visualization.scss"
    ],

    /* Workaround:
       ddionrails-elasticsearch: search library
    */
    elasticsearchInline: glob.sync(
      "./node_modules/ddionrails-elasticsearch/dist/inline.*.bundle.js"
    ),
    elasticsearchPolyfills: glob.sync(
      "./node_modules/ddionrails-elasticsearch/dist/polyfills.*.bundle.js"
    ),
    elasticsearchVendor: glob.sync(
      "./node_modules/ddionrails-elasticsearch/dist/vendor.*.bundle.js"
    ),
    elasticsearchMain: glob.sync(
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
    new MiniCssExtractPlugin({
      filename: "[name].css",
      chunkFilename: "[id].css",
      ignoreOrder: false // Enable to remove warnings about conflicting order
    })
  ],

  module: {
    rules: [
      /* Loads scss files, e.g. Bootstrap */
      {
        test: /\.scss$/,
        use: [
          {
            loader: MiniCssExtractPlugin.loader
          },
          "css-loader"
        ]
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
