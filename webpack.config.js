/* !
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
    search: [
      "./assets/js/search/main.js",
      "./assets/scss/search.scss",
    ],
    topics: ["./assets/js/topics.js", "./assets/scss/topics.scss"],
    concept_table: ["./assets/js/concept_table.js", "./assets/scss/topics.scss"],
    variables: ["./assets/js/variables.js", "./assets/scss/variables.scss"],
    questions: ["./assets/js/questions.js", "./assets/scss/questions.scss"],
    visualization: [
      "./assets/js/visualization.js",
      "./assets/scss/visualization.scss",
    ],
  },
  output: {
    path: path.resolve("./static/dist/"),
    publicPath: "",
    filename: "[name].js",
  },

  plugins: [
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery",
    }),
    new BundleTracker({filename: "./webpack-stats.json"}),
    new MiniCssExtractPlugin({
      filename: "[name].css",
      chunkFilename: "[id].css",
      ignoreOrder: false, // Enable to remove warnings about conflicting order
    }),
    new VueLoaderPlugin(),
    new webpack.DefinePlugin({
      "process.env.ELASTICSEARCH_DSL_INDEX_PREFIX": JSON.stringify(
        process.env.ELASTICSEARCH_DSL_INDEX_PREFIX
      ),
    }),
    // reactivesearch-vue breaks without this.
    // A false value breaks slider ui elements
    new webpack.DefinePlugin({
      "process.browser": true,
    }),
  ],

  module: {
    rules: [
      /* Loads scss files, e.g. Bootstrap */
      {
        test: /\.scss$/,
        use: [
          {
            loader: MiniCssExtractPlugin.loader,
          },
          "css-loader",
          "sass-loader",
        ],
      },
      /* Loads fonts, used for Bootstrap */
      {
        test: /\.(woff(2)?|ttf|eot|svg)$/,
        type: "asset/resource",
        generator: {
          filename: "fonts/[name][ext]",
        },
      },
      /* Loads static files, e.g. images */
      {
        test: /\.(png|jpg|gif|ico)$/,
        type: "asset/resource",
        generator: {
          filename: "[name][ext]",
        },
      },
      /* Loads vue single file components */
      {
        test: /\.vue$/,
        use: "vue-loader",
      },
      /* Loads style block in vue single file components */
      {
        test: /\.css$/,
        use: ["vue-style-loader", "css-loader", "sass-loader"],
      },
    ],
  },
  resolve: {
    extensions: [".js", ".jsx"],
    modules: [path.resolve(__dirname, "node_modules")],
  },
};
