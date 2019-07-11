/*!
 * ddionrails - webpack configuration
 * Copyright 2018-2019
 * Licensed under AGPL (https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md)
 */

"use strict";

const path = require("path");
const webpack = require("webpack");
const BundleTracker = require("webpack-bundle-tracker");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const VueLoaderPlugin = require("vue-loader/lib/plugin");

module.exports = {
  context: __dirname,
  entry: {
    /* css and js libraries for ddionrails */
    index: "./assets/js/index.js",
    search: "./assets/js/search/src/main.js",
    topics: ["./assets/js/topics.js", "./assets/scss/topics.scss"],
    visualization: [
      "./assets/js/visualization.js",
      "./assets/scss/visualization.scss"
    ],
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
    new VueLoaderPlugin(),
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
          "css-loader",
          "sass-loader"
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
      /* Loads static files, e.g. images */
      {
        test: /\.(png|jpg|gif)$/,
        use: [
          {
            loader: "file-loader",
            options: {}
          }
        ]
      },
      /* Loads vue single file components */
      {
        test: /\.vue$/,
        use: "vue-loader"
      },
      /* Loads style block in vue single file components */
      {
        test: /\.css$/,
        use: [
          "vue-style-loader",
          "css-loader"
        ]
      }
    ]
  },
  resolve: {
    extensions: [".js", ".jsx"],
    modules: [path.resolve(__dirname, "node_modules")]
  }
};
