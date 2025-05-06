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
        changeOrigin: true
      }
    }
  },
  
  chainWebpack: config => {
    // 禁用eslint
    config.module.rules.delete('eslint');
    
    // 配置Vue的Feature flag
    config.plugin('define').tap((definitions) => {
      Object.assign(definitions[0]['process.env'], {
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false'
      });
      return definitions;
    });
  },
  
  lintOnSave: false,  // 禁用保存时的lint
  
  // 配置公共路径，确保资源能正确加载
  publicPath: '/static/vue/'
}); 