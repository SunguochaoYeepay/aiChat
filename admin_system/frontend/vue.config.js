const { defineConfig } = require('@vue/cli-service');

module.exports = defineConfig({
  outputDir: '../static/vue',  // 构建输出目录，可以直接输出到 Django 的静态文件目录
  assetsDir: 'assets',         // 放置静态资源的目录
  indexPath: 'index.html',     // 输出的 index.html 文件名
  filenameHashing: false,      // 禁用文件名哈希
  
  devServer: {
    port: 8080,                // 开发服务器端口
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // Django 后端地址
        ws: true,
        changeOrigin: true,
        logLevel: 'debug',     // 添加日志级别，方便调试
        pathRewrite: {
          '^/api': '/api'      // 不做路径重写，保持原始路径
        }
      }
    }
  },
  
  chainWebpack: config => {
    // 禁用eslint
    config.module.rules.delete('eslint');
    
    // 配置Vue的Feature flag
    config.plugin('define').tap((definitions) => {
      Object.assign(definitions[0]['process.env'], {
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false',
        // API URL环境变量，使用'/api'作为基础URL
        VUE_APP_API_URL: '"/api"',  // 设为/api，这样API请求函数中就不需要再加/api前缀
      });
      return definitions;
    });
  },
  
  lintOnSave: false,  // 禁用保存时的lint
  
  // 配置公共路径，确保资源能正确加载
  // 将publicPath改为相对路径，这样vue应用可以通过不同的URL访问
  publicPath: './'
}); 