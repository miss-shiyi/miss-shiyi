import { defineConfig } from 'vitepress'

export default defineConfig({
  title: "拾遗集",
  description: "Digital Garden",
  lang: 'zh-CN',
  lastUpdated: true,
  cleanUrls: true,
  
  themeConfig: {
    logo: 'https://github.com/miss-shiyi.png',
    siteTitle: '漼时宜',
    
    // 顶部导航栏
    nav: [
      { text: '首页', link: '/' },
      { text: '归档', link: '/archive' }
    ],

    // 社交链接
    socialLinks: [
      { icon: 'github', link: 'https://github.com/miss-shiyi/miss-shiyi' }
    ],

    // 搜索功能（原生支持，极其强大）
    search: {
      provider: 'local'
    },

    // 页脚
    footer: {
      message: 'Belong to no one, possess no one.',
      copyright: 'Copyright © 2024-present 漼时宜'
    }
  },

  // Markdown 增强配置
  markdown: {
    lineNumbers: true, // 开启代码行号
    theme: {
      light: 'github-light',
      dark: 'github-dark',
    }
  }
})
