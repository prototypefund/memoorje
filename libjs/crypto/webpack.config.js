const path = require('path')

const distPath = path.resolve(__dirname, 'dist')

module.exports = {
  entry: path.join(distPath, 'index.js'),
  output: {
    filename: 'index.umd.js',
    path: distPath,
    library: {
      name: 'MemoorjeCrypto',
      type: 'umd'
    }
  }
}
