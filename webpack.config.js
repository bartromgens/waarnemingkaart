var path = require("path");
var webpack = require('webpack');
var ManifestPlugin = require('webpack-manifest-plugin');
var WebpackCleanupPlugin = require('webpack-cleanup-plugin');
var ExtractTextPlugin = require("extract-text-webpack-plugin");


module.exports = {
    context: __dirname,
    entry: {
        main: ["./website/js/main.js"],
        css: ["./website/css/custom.css", "./website/css/simple-sidebar.css"],
    },
    output: {
        path: path.join(__dirname, "website/static/dist/"),
        filename: "[name].js"
    },
    module: {
        loaders: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                loader: "babel-loader",
                query: {
                    presets: ['es2015'],
                    compact: false // because I want readable output
                }
            }
        ],
        rules: [
            {
                test: /\.css$/,
                use: ExtractTextPlugin.extract({
                    fallback: "style-loader",
                    use: "css-loader"
                })
            }
        ],
    },
    externals: {
//        jquery: "jQuery"
    },
    plugins: [
        new ManifestPlugin(),
        new ExtractTextPlugin("waarnemingkaart.css"),
        new WebpackCleanupPlugin(),
    ],
};
