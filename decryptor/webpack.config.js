const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const fs = require('fs');

module.exports = {
    entry: './src/index.js',  // Entry point of your application
    devtool: 'inline-source-map',
    devServer: {
        // contentBase: [
        //     path.join(__dirname, 'dist'),
        // ],
        host: '0.0.0.0',
        // inline:true,
        port: 9000,
        https: {
            key: fs.readFileSync(path.join(__dirname, 'ssl/key.pem')),
            cert: fs.readFileSync(path.join(__dirname, 'ssl/cert.pem')),
        },
    },
    output: {
        filename: '[name].[fullhash].bundle.js',
        path: path.resolve(__dirname, 'dist')
    },
    plugins: [
        new CleanWebpackPlugin(),
        new HtmlWebpackPlugin({
            title: 'Decryptor',
            template: './src/assets/index.html',
            filename: 'index.html',
            inject: false,
            // inlineSource: '.(js|css)$',
            // chunks: ['index'],
            minify: false,
        }),
    ],
    module: {
        rules: [
            {
                test: /\.css$/i,
                use: ['style-loader', 'css-loader'],
            },
            {
                test: /\.(png|svg|jpg|jpeg|gif)$/i,
                type: 'asset/resource',
            },
        ],
    },
    resolve: {
        alias: {
            '@src': path.resolve(__dirname, 'src'),
        },
    }
};
