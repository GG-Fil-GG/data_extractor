const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: {
      '/': {
        target: 'http://127.0.0.1:5001',
        changeOrigin: true,
        onProxyReq(proxyReq, req, res) {
          console.log('Proxy request:', req.method, req.url);
        },
        onProxyRes(proxyRes, req, res) {
          console.log('Proxy response:', proxyRes.statusCode, req.url);
        }
      }
    }
  }
})
