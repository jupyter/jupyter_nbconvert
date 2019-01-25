var version = require('./package.json').version;
const path = require('path');
var pyname = 'jupyter-widgets-render'
var postcss = require('postcss');

// Custom webpack loaders are generally the same for all webpack bundles, hence
// stored in a separate local variable.
var rules = [
    // { test: /\.css$/, use: ['style-loader', 'css-loader']},
    {test: /\.png$/,use: 'url-loader?limit=10000000'},
    { test: /\.css$/, use: [
        'style-loader',
        'css-loader',
        {
            loader: 'postcss-loader',
            options: {
                plugins: [
                    postcss.plugin('delete-tilde', function() {
                        return function (css) {
                            css.walkAtRules('import', function(rule) {
                                rule.params = rule.params.replace('~', '');
                            });
                        };
                    }),
                    require('postcss-import')(),
                ]
            }
        }
    ]},
    { test: /\.woff2(\?v=\d+\.\d+\.\d+)?$/, use: 'url-loader?limit=10000&mimetype=application/font-woff' },
    { test: /\.woff(\?v=\d+\.\d+\.\d+)?$/, use: 'url-loader?limit=10000&mimetype=application/font-woff' },
    { test: /\.ttf(\?v=\d+\.\d+\.\d+)?$/, use: 'url-loader?limit=10000&mimetype=application/octet-stream' },
    { test: /\.eot(\?v=\d+\.\d+\.\d+)?$/, use: 'file-loader' },
    { test: /\.svg(\?v=\d+\.\d+\.\d+)?$/, use: 'url-loader?limit=10000&mimetype=image/svg+xml' }

    // { test: /\.js$/, loader: 'babel-loader', exclude: /node_modules/},
    // { test: /\.(ts|js)?$/, use: [
    //      { loader: 'cache-loader' },
    //      {
    //                 loader: 'thread-loader',
    //                 options: {
    //                     // there should be 1 cpu for the fork-ts-checker-webpack-plugin
    //                     workers: require('os').cpus().length - 1,
    //                 },
    //      },
    //      { loader: "ts-loader", options: {transpileOnly: true,happyPackMode: true} }
    //     ]}
];

var resolve =  {
    extensions: ['.ts', '.js']
};


module.exports = [
    {   entry: './lib/index.js',
        devtool: 'inline-source-map',
        output: {
            filename: 'snapshot.js',
            path: path.resolve(__dirname, `nbconvert/resources`),
            libraryTarget: 'amd'
        },
        devtool: 'source-map',
        module: {
            rules: rules
        },
        // externals: ['@jupyter-widgets/base', '@jupyter-widgets/controls'],
        resolve: resolve
    },
];
