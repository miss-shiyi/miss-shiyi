import { defineConfig } from 'vitepress'
// 导入由 Python 脚本生成的侧边栏文件
import sidebar from './sidebar.json'

export default defineConfig({
  // 重要：如果你的仓库名是 miss-shiyi，这里必须完全匹配
  base: '/miss-shiyi/', 
  
  title: "拾遗集",
  description: "Digital Garden",
  lang: 'zh-CN',
  
  // 即使刷新也能保持洁净的 URL（隐藏 .html 后缀）
  cleanUrls: true,
  
  // 开启最后更新时间显示
  lastUpdated: true,

  themeConfig: {
    // 你的 GitHub 头像作为 Logo
    logo: 'https://github.com/miss-shiyi.png',
    siteTitle: '漼时宜',

    // 导航栏配置
    nav: [
      { text: '首页', link: '/' },
      { text: '全部分类', link: '/README' }
    ],

    // 核心：直接引用 Python 脚本生成的侧边栏数据
    sidebar: sidebar,

    // 社交链接
    socialLinks: [
      { icon: 'github', link: 'https://github.com/miss-shiyi/miss-shiyi' }
    ],

    // 本地搜索功能（无需配置第三方服务，体验极佳）
    search: {
      provider: 'local',
      options: {
        translations: {
          button: {
            buttonText: '搜索文档',
            buttonAriaLabel: '搜索文档'
          },
          modal: {
            noResultsText: '无法找到相关结果',
            resetButtonTitle: '清除查询条件',
            footer: {
              selectText: '选择',
              navigateText: '切换'
            }
          }
        }
      }
    },

    // 页面底部配置
    footer: {
      message: 'Belong to no one, possess no one. Expect less, live more.',
      copyright: 'Copyright © 2024-2026 漼时宜'
    },

    // 侧边栏和正文中的编辑/更新文案
    outline: {
      label: '本页目录',
      level: [2, 3]
    },
    lastUpdatedText: '最后更新于',
    docFooter: {
      prev: '上一篇',
      next: '下一篇'
    }
  },

  // Markdown 增强渲染配置
  markdown: {
    lineNumbers: true, // 显示行号
    theme: {
      light: 'github-light',
      dark: 'github-dark'
    }
  }
})
