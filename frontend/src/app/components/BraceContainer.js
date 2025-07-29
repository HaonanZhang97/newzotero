// components/BraceContainer.jsx
import { useState, useEffect, useRef } from 'react';
import styles from './BraceContainer.module.css'; // 确保你有对应的CSS样式文件

const BraceContainer = ({ items, initialVisibleCount = 1, children }) => {
    const [visibleItems, setVisibleItems] = useState(initialVisibleCount);
    const [isExpanded, setIsExpanded] = useState(false);
    const containerRef = useRef(null);
    const braceRef = useRef(null);

    // 动态调整大括号高度
    useEffect(() => {
        if (containerRef.current && braceRef.current) {
            const containerHeight = containerRef.current.scrollHeight;
            braceRef.current.style.setProperty('--brace-height', `${containerHeight}px`);
        }
    }, [visibleItems, items, children]);

    const toggleExpand = () => {
        if (isExpanded) {
            setVisibleItems(initialVisibleCount);
        } else {
            setVisibleItems(items.length);
        }
        setIsExpanded(!isExpanded);
    };

    return (
        <div className={styles['brace-component']}>
            <div className={styles['brace-container']}>
                {/* 左侧大括号 */}
                <div className={styles['brace']} ref={braceRef}>
                    <div className={styles['brace-top']}></div>
                    <div className={styles['brace-middle']}></div>
                    <div className={styles['brace-bottom']}></div>
                </div>
                {/* 内容区域 */}
                <div className={styles['content-container']} ref={containerRef}>
                    {children}
                    {items.slice(0, visibleItems).map((item, index) => (
                        <div key={index} className={styles['entry-item']}>
                            {item.onDelete && (
                                <button
                                    style={{ color: "#d32f2f", border: "none", background: "none", cursor: "pointer", fontSize: 12, marginLeft: 8 }}
                                    onClick={item.onDelete}
                                >删除</button>
                            )}
                            <div className={styles['entry-icon']}>📚</div>
                            <div className={styles['entry-details']}>
                                <h3 className={styles['entry-title']}>{item.title}</h3>
                                <p className={styles['entry-description']}>{item.description}</p>
                                <div className={styles['entry-meta']}>
                                    <span className={styles['entry-author']}>{item.author}</span>
                                    <span className={styles['entry-date']}>{item.date}</span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
            {/* 展开/收起按钮 */}
            {items.length > initialVisibleCount && (
                <button
                    className={styles['expand-button'] + (isExpanded ? ' ' + styles['expanded'] : '')}
                    onClick={toggleExpand}
                >
                    {isExpanded ? '收起' : '展开'}
                    <span className={styles['arrow']}>{isExpanded ? '▲' : '▼'}</span>
                </button>
            )}
        </div>
    );
};

export default BraceContainer;