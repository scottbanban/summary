/**
 * 个人博客网站 JavaScript
 * 提供基础交互功能和用户体验增强
 */

// 等待DOM加载完成
document.addEventListener('DOMContentLoaded', function() {
    initApp();
});

/**
 * 应用初始化
 */
function initApp() {
    console.log('📱 个人博客网站正在初始化...');

    // 初始化工具提示
    initTooltips();

    // 初始化缓存状态显示
    initCacheStatus();

    // 初始化点击波纹效果
    initRippleEffect();

    // 初始化滚动动画
    initScrollAnimations();

    // 初始化分享功能
    initShareFunctions();

    // 初始化收藏功能
    initBookmarkFunctions();

    // 页面加载完成提示
    setTimeout(() => {
        console.log('✅ 应用初始化完成');
    }, 100);
}

/**
 * 初始化工具提示
 */
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');

    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function(e) {
            const tooltipText = this.getAttribute('data-tooltip');
            if (!tooltipText) return;

            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = tooltipText;
            tooltip.style.position = 'absolute';
            tooltip.style.backgroundColor = '#c82506';
            tooltip.style.color = 'white';
            tooltip.style.padding = '4px 8px';
            tooltip.style.borderRadius = '4px';
            tooltip.style.fontSize = '12px';
            tooltip.style.zIndex = '10000';
            tooltip.style.whiteSpace = 'nowrap';

            document.body.appendChild(tooltip);

            const rect = this.getBoundingClientRect();
            tooltip.style.top = (rect.top - tooltip.offsetHeight - 8) + 'px';
            tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';

            this._currentTooltip = tooltip;
        });

        element.addEventListener('mouseleave', function() {
            if (this._currentTooltip) {
                this._currentTooltip.remove();
                this._currentTooltip = null;
            }
        });
    });
}

/**
 * 初始化缓存状态显示
 */
function initCacheStatus() {
    const cacheBadge = document.getElementById('cache-status');
    if (!cacheBadge) return;

    function updateCacheStatus() {
        fetch('/api/health')
            .then(response => response.json())
            .then(data => {
                const cacheSize = data.cache_size || 0;
                cacheBadge.textContent = `缓存: ${cacheSize} 条`;
                cacheBadge.title = `缓存中有 ${cacheSize} 条记录，点击刷新`;
            })
            .catch(error => {
                console.error('获取缓存状态失败:', error);
                cacheBadge.textContent = '缓存: 未知';
            });
    }

    // 初始更新
    updateCacheStatus();

    // 每隔30秒更新一次
    setInterval(updateCacheStatus, 30000);

    // 点击刷新
    cacheBadge.addEventListener('click', updateCacheStatus);
}

/**
 * 初始化点击波纹效果
 */
function initRippleEffect() {
    // 为按钮添加涟漪效果
    const buttons = document.querySelectorAll('.btn');

    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (this.classList.contains('no-ripple')) return;

            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.style.position = 'absolute';
            ripple.style.borderRadius = '50%';
            ripple.style.background = 'rgba(255, 255, 255, 0.4)';
            ripple.style.transform = 'scale(0)';
            ripple.style.animation = 'ripple 600ms linear';

            this.style.position = 'relative';
            this.style.overflow = 'hidden';

            this.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // 添加涟漪动画关键帧
    if (!document.querySelector('#ripple-animation')) {
        const style = document.createElement('style');
        style.id = 'ripple-animation';
        style.textContent = `
            @keyframes ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * 初始化滚动动画
 */
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '50px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');

                // 如果是文章卡片，添加顺序动画
                if (entry.target.classList.contains('article-item')) {
                    const index = Array.from(document.querySelectorAll('.article-item')).indexOf(entry.target);
                    entry.target.style.animationDelay = `${index * 100}ms`;
                }
            }
        });
    }, observerOptions);

    // 观察文章卡片和特性卡片
    document.querySelectorAll('.article-item, .feature-card, .highlight-block').forEach(el => {
        observer.observe(el);
    });

    // 添加动画样式
    if (!document.querySelector('#scroll-animations')) {
        const style = document.createElement('style');
        style.id = 'scroll-animations';
        style.textContent = `
            .article-item, .feature-card, .highlight-block {
                opacity: 0;
                transform: translateY(20px);
                transition: opacity 0.6s ease, transform 0.6s ease;
            }

            .article-item.visible, .feature-card.visible, .highlight-block.visible {
                opacity: 1;
                transform: translateY(0);
            }

            .article-item.visible {
                animation: slideUp 0.6s ease forwards;
            }

            @keyframes slideUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * 初始化分享功能
 */
function initShareFunctions() {
    window.shareArticle = function(articleId) {
        const articleElement = document.querySelector(`#article-${articleId}`);
        if (!articleElement) return;

        const title = articleElement.querySelector('.article-title').textContent.trim();
        const url = window.location.origin + '/article/' + articleId;

        // 使用Web Share API（现代浏览器支持）
        if (navigator.share) {
            navigator.share({
                title: title,
                text: '阅读这篇来自飞书博客的文章',
                url: url
            })
            .then(() => console.log('分享成功'))
            .catch((error) => console.log('分享失败:', error));
        } else {
            // 回退方案：复制链接到剪贴板
            navigator.clipboard.writeText(url)
                .then(() => {
                    alert('文章链接已复制到剪贴板');
                })
                .catch(() => {
                    // 不支持clipboard API，显示链接
                    prompt('复制以下链接分享：', url);
                });
        }
    };

    // 为所有分享按钮绑定事件
    document.querySelectorAll('.share-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            const articleId = this.closest('.article-item')?.id?.replace('article-', '') ||
                             this.closest('.article-detail')?.querySelector('[data-article-id]')?.getAttribute('data-article-id');
            if (articleId) {
                shareArticle(articleId);
            }
        });
    });
}

/**
 * 初始化收藏功能
 */
function initBookmarkFunctions() {
    window.bookmarkArticle = function(articleId) {
        const articleElement = document.querySelector(`#article-${articleId}`);
        const title = articleElement?.querySelector('.article-title')?.textContent.trim() || '未知文章';

        // 获取或初始化收藏列表
        let bookmarks = JSON.parse(localStorage.getItem('blog_bookmarks') || '[]');

        // 检查是否已收藏
        const existingIndex = bookmarks.findIndex(item => item.id === articleId);

        let message;
        if (existingIndex === -1) {
            // 添加收藏
            const bookmark = {
                id: articleId,
                title: title,
                url: window.location.origin + '/article/' + articleId,
                addedAt: new Date().toISOString()
            };
            bookmarks.unshift(bookmark);
            message = '文章已收藏! 💾';

            // 更新按钮状态
            const button = document.querySelector(`[onclick*="bookmarkArticle('${articleId}')"]`);
            if (button) {
                button.innerHTML = '<i class="fas fa-bookmark"></i> 已收藏';
                button.classList.add('bookmarked');
            }
        } else {
            // 移除收藏
            bookmarks.splice(existingIndex, 1);
            message = '已取消收藏';

            // 更新按钮状态
            const button = document.querySelector(`[onclick*="bookmarkArticle('${articleId}')"]`);
            if (button) {
                button.innerHTML = '<i class="fas fa-bookmark"></i> 收藏';
                button.classList.remove('bookmarked');
            }
        }

        // 保存到localStorage（最多保存50条）
        bookmarks = bookmarks.slice(0, 50);
        localStorage.setItem('blog_bookmarks', JSON.stringify(bookmarks));

        // 显示反馈
        showToast(message);

        // 更新收藏计数显示
        updateBookmarkCount();
    };

    // 为每个按钮设置初始状态
    document.querySelectorAll('.bookmark-btn').forEach(button => {
        const match = button.getAttribute('onclick')?.match(/bookmarkArticle\('([^']+)'\)/);
        if (match) {
            const articleId = match[1];
            const bookmarks = JSON.parse(localStorage.getItem('blog_bookmarks') || '[]');
            const isBookmarked = bookmarks.some(item => item.id === articleId);

            if (isBookmarked) {
                button.innerHTML = '<i class="fas fa-bookmark"></i> 已收藏';
                button.classList.add('bookmarked');
            }
        }
    });

    // 初始更新收藏计数
    updateBookmarkCount();
}

/**
 * 更新收藏计数显示
 */
function updateBookmarkCount() {
    const countBadge = document.getElementById('bookmark-count');
    if (!countBadge) return;

    const bookmarks = JSON.parse(localStorage.getItem('blog_bookmarks') || '[]');
    countBadge.textContent = bookmarks.length;

    // 添加悬停效果显示收藏列表
    if (bookmarks.length > 0) {
        updateBookmarkTooltip();
    }
}

/**
 * 更新收藏工具提示
 */
function updateBookmarkTooltip() {
    const countBadge = document.getElementById('bookmark-count');
    if (!countBadge) return;

    const bookmarks = JSON.parse(localStorage.getItem('blog_bookmarks') || '[]');

    countBadge.removeAttribute('data-tooltip');
    countBadge.setAttribute('data-tooltip',
        bookmarks.slice(0, 3).map(item => item.title).join('\n') +
        (bookmarks.length > 3 ? `\n... 还有${bookmarks.length - 3}条` : '')
    );
}

/**
 * 显示Toast通知
 */
function showToast(message, duration = 3000) {
    // 移除已存在的toast
    const existingToast = document.querySelector('.toast-notification');
    if (existingToast) {
        existingToast.remove();
    }

    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: var(--color-primary);
        color: white;
        padding: 12px 24px;
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-lg);
        z-index: 10000;
        opacity: 0;
        transform: translateY(20px);
        transition: opacity 0.3s, transform 0.3s;
        word-wrap: break-word;
        max-width: 300px;
        animation: toast-fade-in 0.3s ease forwards;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);

    // 添加动画样式
    if (!document.querySelector('#toast-animation')) {
        const style = document.createElement('style');
        style.id = 'toast-animation';
        style.textContent = `
            @keyframes toast-fade-in {
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        `;
        document.head.appendChild(style);
    }

    // 自动隐藏
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(20px)';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * 添加额外的事件监听
 */
document.addEventListener('keydown', function(e) {
    // Esc键关闭弹窗等
    if (e.key === 'Escape') {
        // 可以在这里添加关闭模态框的逻辑
        console.log('Esc键按下');
    }

    // Ctrl+D 收藏当前文章（如果存在）
    if (e.ctrlKey && e.key === 'd') {
        e.preventDefault();
        const articleId = window.location.pathname.split('/').pop();
        if (articleId && articleId !== '') {
            window.bookmarkArticle?.(articleId);
        }
    }
});

// 添加全局错误处理
window.addEventListener('error', function(e) {
    console.error('全局错误:', e.error);

    // 可以在这里添加错误报告逻辑
    if (window.location.hostname === 'localhost' && e.message) {
        showToast(`脚本错误: ${e.message}`, 5000);
    }
});

// 添加离线检测
window.addEventListener('online', () => {
    showToast('网络已恢复连接');
});

window.addEventListener('offline', () => {
    showToast('网络已断开，部分功能可能不可用', 5000);
});

console.log('🎯 main.js 加载完成，准备就绪！');