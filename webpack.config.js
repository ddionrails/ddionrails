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

const config = {
  context: __dirname,
  entry: {
    /* css and js libraries for ddionrails */
    index: ["./assets/js/index.ts", "./assets/scss/index.scss"],
    instrument_table: ["./assets/js/tables/instrument_table.ts"],
    table_attachment: ["./assets/scss/table_attachment.scss"],
    basket: "./assets/scss/basket.scss",
    basket_button: "./assets/js/basket_button.ts",
    basket_view_variable_buttons: "./assets/js/basket_view_variable_buttons.ts",
    variable_view_basket_button: "./assets/js/variable_view_basket_button.ts",
    variable_labels: "./assets/js/tables/variable_labels.ts",
    dataset_table: "./assets/js/tables/dataset_table.ts",
    variable_table: "./assets/js/tables/variable_table.ts",
    question_table: "./assets/js/tables/question_table.ts",
    search: ["./assets/js/search/main.js", "./assets/scss/search.scss"],
    topics: ["./assets/js/topics.js", "./assets/scss/topics.scss"],
    concept_table: [
      "./assets/js/tables/concept_table.ts",
      "./assets/scss/topics.scss",
    ],
    feedback: ["./assets/js/feedback.ts"],
    statistics: ["./assets/scss/statistics.scss"],
    statistics_navigation: [
      "./assets/js/statistics_navigation.ts",
      "./assets/scss/statistics_navigation.scss",
    ],
    focus_anchor: ["./assets/js/focus_anchor.ts"],
    question_images: ["./assets/js/question_images.ts"],
    questions: ["./assets/js/questions.ts", "./assets/scss/questions.scss"],
    question_comparison: [
      "./assets/js/question_comparison.ts",
      "./assets/scss/question_comparison.scss",
    ],
    description_modal: [
      "./assets/js/description_modal.ts",
      "./assets/scss/description_modal.scss",
    ],
    variables: ["./assets/scss/variables.scss"],
    visualization: [
      "./assets/js/visualization.js",
      "./assets/scss/visualization.scss",
    ],
  },
  output: {
    path: path.resolve("./static/dist/"),
    publicPath: "",
    // filename is defined later; value depends on mode
  },

  plugins: [
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery",
    }),
    new BundleTracker({filename: "./webpack-stats.json"}),
    new VueLoaderPlugin(),
    new webpack.DefinePlugin({
      "process.env.ELASTICSEARCH_DSL_INDEX_PREFIX": JSON.stringify(
        process.env.ELASTICSEARCH_DSL_INDEX_PREFIX
      ),
      "process.env.SHOW_STATISTICS": JSON.stringify(
        process.env.SHOW_STATISTICS
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
      /* Typescript? */
      {
        test: /\.tsx?$/,
        use: "ts-loader",
        exclude: /node_modules/,
      },
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
    extensions: [".js", ".jsx", ".ts", ".tsx"],
    modules: [path.resolve(__dirname, "node_modules")],
  },
};

module.exports = (env, argv) => {
  let cssFilename = "";
  let chunkFilename = "";
  const hashFormat = ".[contenthash]";
  if (argv.mode === "development") {
    config["output"]["filename"] = "[name].js";
    cssFilename = "[name].css";
    chunkFilename = "[id].css";
  } else {
    config["output"]["filename"] = `[name]${hashFormat}.js`;
    cssFilename = `[name]${hashFormat}.css`;
    chunkFilename = `[id]${hashFormat}.css`;
  }

  config["plugins"].push(
    new MiniCssExtractPlugin({
      filename: cssFilename,
      chunkFilename,
      ignoreOrder: false, // Enable to remove warnings about conflicting order
    })
  );

  return config;
};
