'use client';
import { Libre_Baskerville } from "next/font/google";
import { useState, useRef } from "react";
import Link from "next/link";
import "./page.css";

const libreBaskerville = Libre_Baskerville({
  weight: ['400', '700'], // 需要的字重
  style: ['normal', 'italic'], // 需要的样式
  subsets: ['latin'], // 语言子集
  display: 'swap', // 确保文本在字体加载时可见
});

export default function NoteBrowsePage() {


  const [searchQuery, setSearchQuery] = useState("");
  const [resultsPerPage, setResultsPerPage] = useState("5");
  const [hasSearched, setHasSearched] = useState(false);
  const [searchResults, setSearchResults] = useState([]);

  // 下载文件
  const handleDownload = async (fileId, fileName) => {
    try {
      const username = typeof window !== "undefined" ? localStorage.getItem("username") : "";
      const response = await fetch(`/api/download/${fileId}?username=${encodeURIComponent(username)}`, {
        method: 'GET',
      });

      if (!response.ok) {
        const error = await response.json();
        alert(`下载失败: ${error.error || '未知错误'}`);
        return;
      }

      // 创建下载链接
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('下载文件时出错:', error);
      alert('下载文件失败，请重试');
    }
  };

  console.log(resultsPerPage, 'resultsPerPage');

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      return;
    }
    setHasSearched(true);

    const username = typeof window !== "undefined" ? localStorage.getItem("username") : "";

    let resultsNum = resultsPerPage === "all" ? 100 : Number(resultsPerPage);
    try {
      const res = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: searchQuery,
          resultsPerPage: resultsNum,
          username // 加上用户名
        })
      });
      if (!res.ok) throw new Error('搜索失败');
      const data = await res.json();
      console.log('搜索结果:', data);
      setSearchResults(data.results || []);
    } catch (err) {
      setSearchResults([]);
      alert('搜索出错，请稍后重试');
    }
  };


  return (
    <div
      style={{
        minHeight: "100vh",
        width: "100%",
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        background: "#fff",
        margin: 0,
        padding: 0,
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* 顶部栏 */}
      <div
        style={{
          background: "#fff",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "2vh 3vw 0 3vw",
          position: "relative",
          height: "12vh",
          minHeight: "80px",
          boxSizing: "border-box",
        }}
      >
        <Link href="/">
          <div
            style={{
              position: "absolute",
              top: "50%",
              left: "5vw",
              transform: "translateY(-50%)",
              fontWeight: "bold",
              color: "#111",
            }}
          >
            <div style={{ fontSize: "clamp(24px, 3vw, 32px)", marginBottom: "0.5vh" }}>NewZotero</div>
            <div style={{ fontSize: "clamp(14px, 1.8vw, 18px)", opacity: 0.8 }}>v0.1.22 知识库管理助手</div>
          </div>
        </Link>
        <div style={{ position: "absolute", top: "50%", right: "5vw", transform: "translateY(-50%)", display: "flex", gap: "1.5vw" }}>
          <Link href="/library">
            <button className="library-button">
              笔记写入
            </button>
          </Link>
          <button
            style={{
              background: "#111",
              color: "#fff",
              border: "none",
              borderRadius: "6px",
              padding: "1vh 2vw",
              fontSize: "clamp(16px, 2vw, 24px)",
              fontWeight: "bold",
              cursor: "default",
            }}
            disabled={true}
          >
            笔记搜索
          </button>
        </div>
      </div>
      {/* 主体内容 */}
      <div
        style={{
          justifyContent: "center",
          alignItems: "center",
          width: "100%",
          zIndex: 10,
          transition: "all 0.4s cubic-bezier(.4,2,.6,1)",
          transform: hasSearched ? "scale(0.8)" : "none",
          transformOrigin: "center",
          //  marginLeft: hasSearched ? "30vw" : "0",
        }}
      >
        {/* 主体内容 */}
        {!hasSearched && (
          <div
            className={libreBaskerville.className}
            style={{
              flex: 1,
              display: "flex",
              marginTop: "6vh",
              justifyContent: "center",
              padding: "2vh",
              fontSize: "clamp(32px, 6vw, 80px)",
            }}>
            What's your next research topic?
          </div>
        )}
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", width: "100%" }}>
          <div style={{ width: "min(90vw, 1200px)" }}>
            <input
              className="center-placeholder"
              type="text"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              onKeyDown={e => {
                if (e.key === 'Enter') {
                  handleSearch();
                }
              }}
              placeholder={hasSearched ? "What's your next research topic?" : "输入你想搜索的研究idea,例如：庄子如何看待痛苦"}
              style={{
                width: "100%",
                padding: "1vh 1.5vw",
                fontSize: "clamp(16px, 2vw, 24px)",
                border: "2px dashed #000",
                borderRadius: "4px",
                marginTop: hasSearched ? "2%" : "2vh",
              }}
            />
            <div style={{ display: "flex", alignItems: "center", marginTop: "1.5vh" }}>
              <span style={{ fontSize: "clamp(14px, 1.8vw, 20px)", marginRight: "1vw" }}>返回最多匹配数：</span>
              <select
                onChange={e => setResultsPerPage(e.target.value)}
                style={{
                  width: "clamp(60px, 8vw, 120px)",
                  padding: "1vh 1vw",
                  fontSize: "clamp(16px, 2vw, 24px)",
                  border: "none",
                  borderRadius: "4px",
                  textAlign: "center"
                }}
                defaultValue="5"
              >
                <option value="3">3</option>
                <option value="5">5</option>
                <option value="10">10</option>
                <option value="20">20</option>
                <option value="all">all</option>
              </select>
            </div>
            {!hasSearched && (<div style={{ display: "flex", alignItems: "center", marginTop: "1vh" }}>
              <span style={{ fontSize: "clamp(12px, 1.6vw, 20px)", marginRight: "1vw", color: "#828282" }}>
                如何使用该功能：<br />
                · 输入任何你感兴趣的想法或问题，模型将会自动为你寻找和你的问题最相关的旧笔记！<br />
                · 匹配的回复将按照 “相似度评分” 从低到高排行；<br />
                · “相似度评分” 类似于回归值，数字越小意味着与问题越相关。<br />
              </span>
            </div>)}
            {hasSearched && searchResults.length > 0 && (
              <div
                className="hide-scrollbar"
                style={{
                  marginTop: "3vh",
                  width: "100%",
                  maxWidth: "100%",
                  maxHeight: "75vh",
                  overflowY: "auto",
                  overflowX: "hidden",
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center"
                }}
              >
                {searchResults.map((item, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      width: "100%",
                      backgroundColor: item.type === "abstract" ? "#fafafa" : "#cccccc",
                      border: "1px solid #e0e0e0",
                      marginBottom: "2vh",
                      boxShadow: "0 2px 8px rgba(0,0,0,0.03)",
                      padding: "2vh",
                      backgroundImage:
                        item.type === "abstract" ?
                          `linear-gradient(to right, #e0e0e0 1px, transparent 1px),
                          linear-gradient(to bottom, #e0e0e0 1px, transparent 1px) `
                          :
                          `linear-gradient(to right, #a0a0a0 1px, transparent 1px),
                          linear-gradient(to bottom, #a0a0a0 1px, transparent 1px) `,
                      backgroundSize: "15px 15px",
                      gap: "1.5vh",
                    }}
                  >
                    {/* 内容部分 */}
                    <div style={{
                      fontSize: "clamp(14px, 1.6vw, 18px)",
                      color: "#222",
                      lineHeight: 1.8,
                      wordBreak: "break-word",
                      marginBottom: "1vh"
                    }}>
                      <b>内容：</b>{item.content}
                    </div>

                    {/* 元信息部分 */}
                    <div style={{
                      display: "grid",
                      gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                      gap: "1vh 2vw",
                      fontSize: "clamp(12px, 1.3vw, 15px)",
                      color: "#444"
                    }}>
                      <div style={{ wordBreak: "break-word" }}>
                        <b>标题：</b>
                        <span style={{ display: "inline-block", maxWidth: "100%" }}>{item.title}</span>
                      </div>
                      <div style={{ wordBreak: "break-word" }}>
                        <b>作者：</b>
                        <span style={{ display: "inline-block", maxWidth: "100%" }}>{item.author}</span>
                      </div>
                      <div style={{ wordBreak: "break-word" }}>
                        <b>发表日期：</b>
                        <span style={{ display: "inline-block", maxWidth: "100%" }}>{item.date}</span>
                      </div>
                      <div style={{ wordBreak: "break-word" }}>
                        <b>相似度评分：</b>
                        <span style={{ display: "inline-block", maxWidth: "100%" }}>{item.score}</span>
                      </div>

                      {/* 下载按钮（仅对可下载文件显示） */}
                      {item.fileDownloadable && item.fileId && (
                        <div style={{ gridColumn: "span 2", justifySelf: "start" }}>
                          <button
                            onClick={() => handleDownload(item.fileId, item.fileTitle)}
                            style={{
                              background: "#4caf50",
                              color: "white",
                              border: "none",
                              borderRadius: "4px",
                              padding: "0.8vh 1.5vw",
                              fontSize: "clamp(12px, 1.2vw, 14px)",
                              cursor: "pointer",
                              fontWeight: "bold",
                            }}
                            title="下载相关文件"
                          >
                            📄 下载文件
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}