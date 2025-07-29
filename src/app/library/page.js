'use client';
import Image from "next/image";
import Link from "next/link";
import { useRef, useState, useEffect, use } from "react";
import BraceContainer from "../components/BraceContainer";
import "./page.css";


export default function LibraryPage() {

  const username = typeof window !== "undefined" ? localStorage.getItem("username") : "";

  const [files, setFiles] = useState([]);
  const [selectedFileIndex, setSelectedFileIndex] = useState(null);
  const [abstractEntries, setAbstractEntries] = useState({
    title: "",
    author: "",
    date: "",
    page: "",
    content: "",
  });
  const [freeNoteContent, setFreeNoteContent] = useState("");
  const [doi, setDoi] = useState("");
  const [doiError, setDoiError] = useState("");
  const [noteExpanded, setNoteExpanded] = useState(false);
  const [notes, setNotes] = useState([]);
  const fileInputRef = useRef(null);

  // 测量input宽度变化
  const titleSpan = useRef(null);
  const authorSpan = useRef(null);
  const dateSpan = useRef(null);
  const pageSpan = useRef(null);

  const [inputWidths, setInputWidths] = useState({
    title: 0,
    author: 0,
    date: 0,
    page: 0,
  });


  useEffect(() => {
    setInputWidths({
      title: Math.max(titleSpan.current?.offsetWidth + 15 || 40, 40),
      author: Math.max(authorSpan.current?.offsetWidth + 15 || 40, 40),
      date: Math.max(dateSpan.current?.offsetWidth + 15 || 40, 40),
      page: Math.max(pageSpan.current?.offsetWidth + 15 || 40, 40),
    });
  }, [abstractEntries.title, abstractEntries.author, abstractEntries.date, abstractEntries.page]);

  // 加载已有文件
  useEffect(() => {
    if (!username) return;
    fetch(`/api/files?username=${encodeURIComponent(username)}`)
      .then((res) => res.json())
      .then((data) => {
        setFiles(data || []);
        if (data.length > 0) {
          setSelectedFileIndex(0);
          setAbstractEntries({
            ...data[0].meta,
            content: "",
          });
          // 加载所有 notes（不带 fileId，拿到所有 free 和 abstract）
          fetch(`/api/notes?username=${encodeURIComponent(username)}`)
            .then(res => res.json())
            .then(notesData => setNotes(notesData || []));
        }
      });
  }, [username]);


  const handleEntryChange = (e) => {
    setAbstractEntries({ ...abstractEntries, [e.target.name]: e.target.value });
  }

  // 添加摘录
  const handleAddNote = async () => {
    if (!abstractEntries.content.trim() || selectedFileIndex == null) return;
    const file = files[selectedFileIndex];
    const newNote = {
      id: Date.now() + Math.random(),
      fileId: file.id,
      content: abstractEntries.content,
      createdAt: new Date().toISOString(),
      type: "abstract",
      title: abstractEntries.title,
      author: abstractEntries.author,
      date: abstractEntries.date,
      page: abstractEntries.page
    };
    // 1. 本地更新
    setNotes(prev => [...prev, newNote]);
    setAbstractEntries({ ...abstractEntries, content: "" });
    // 2. 同步到后端
    await fetch('/api/notes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...newNote, username })
    });
  };

  // 删除摘录
  const handleDeleteNote = async (noteId) => {
    // 1. 本地更新
    setNotes(prev => prev.filter(n => n.id !== noteId));
    // 2. 同步到后端
    await fetch('/api/notes', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: noteId, username })
    });
  };

  // 拖拽上传
  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    alert("文件上传功能还在开发中");
    return;
    // const droppedFiles = Array.from(e.dataTransfer.files).filter(
    //   (file) =>
    //     file.name.toLowerCase().endsWith(".pdf") ||
    //     file.name.toLowerCase().endsWith(".docx")
    // );
    // if (droppedFiles.length > 0) {
    //   setFiles((prev) => [...prev, ...droppedFiles]);
    // }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  // 点击上传
  const handleFileChange = async (e) => {
    // const selectedFiles = Array.from(e.target.files).filter(
    //   (file) =>
    //     file.name.toLowerCase().endsWith(".pdf") ||
    //     file.name.toLowerCase().endsWith(".docx")
    // );
    // for (const file of selectedFiles) {
    //   const res = await fetch('/api/parse_pdf', {
    //     method: 'POST',
    //     body: JSON.stringify({ title: file.name }),
    //     headers: { 'Content-Type': 'application/json' }
    //   });
    //   const meta = await res.json();
    //   const newFile = {
    //     id: Date.now() + Math.random() + file.name.replace(/[\/\\]/g, "_"),
    //     title: file.name,
    //     meta: { ...meta, type: 'pdf' },
    //     notes: []
    //   };
    //   // 同步到后端
    //   await fetch('/api/files', {
    //     method: 'POST',
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify({ ...newFile, username })
    //   });
    //   setFiles(prev => {
    //     const updated = [...prev, newFile];
    //     setSelectedFileIndex(updated.length - 1);
    //     setAbstractEntries({
    //       ...newFile.meta,
    //       content: "",
    //     });
    //     setNotes([]);
    //     return updated;
    //   });
    // }
    // e.target.value = "";
    alert("文件上传功能还在开发中");
    return;
  };

  // 删除文件
  const handleDelete = async (idx) => {
    const fileToDelete = files[idx];
    // 1. 删除文件
    await fetch('/api/files', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: fileToDelete.id, username })
    });
    // 2. 删除该文件的所有notes
    await fetch('/api/notes', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fileId: fileToDelete.id, username }) // ★加 username
    });
    // 3. 本地更新
    const newFiles = files.filter((_, i) => i !== idx);
    setFiles(newFiles);

    // 4. 如果还有文件，切换到第一个文件并加载其notes
    if (newFiles.length > 0) {
      setSelectedFileIndex(0);
      setAbstractEntries({
        ...newFiles[0].meta,
        content: "",
      });
      // 加载新文件的notes
      fetch(`/api/notes?fileId=${newFiles[0].id}&username=${encodeURIComponent(username)}`)
        .then(res => res.json())
        .then(notesData => setNotes(notesData || []));
    } else {
      // 没有文件了，清空内容
      setSelectedFileIndex(null);
      setAbstractEntries({
        title: "",
        author: "",
        date: "",
        page: "",
        content: "",
      });
      setNotes([]);
    }
  };

  // 当前选中文件
  const selectedFile = files.find(f => f.id === selectedFileIndex);

  // 文件图标
  const getIcon = (name) => {
    if (name.toLowerCase().endsWith(".pdf")) return "/pdf_icon.svg";
    if (name.toLowerCase().endsWith(".docx")) return "/docx_icon.svg";
    return "/file_icon.svg";
  };

  const fetchDoiInfo = async () => {
    setDoiError("");
    if (!doi) {
      setDoiError("请输入有效的DOI");
      return;
    }
    try {
      const response = await fetch(`https://api.crossref.org/works/${encodeURIComponent(doi)}`);
      if (!response.ok) throw new Error("未查到该DOI信息");
      const data = await response.json();

      const newFile = {
        id: Date.now() + Math.random() + doi.replace(/[\/\\]/g, "_"),
        title: data.message.title[0] || "DOI文献",
        meta: {
          title: data.message.title[0] || "",
          author: data.message.author
            ? data.message.author.map(a =>
              [a.family, a.given].filter(Boolean).join(" ")
            ).join(", ")
            : "",
          date: data.message.created?.["date-time"] || "",
          page: "",
          type: 'doi'
        }
      };
      console.log(newFile.id);
      // 存到后端
      await fetch('/api/files', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...newFile, username }) // ★加 username
      });
      // 本地更新并自动选中新文件
      setFiles(prev => {
        const updated = [...prev, newFile];
        setSelectedFileIndex(updated.length - 1); // 选中新加的
        setAbstractEntries({
          ...newFile.meta,
          content: "",
        });
        setNotes([]); // 新文件无 notes
        return updated;
      });
    } catch (error) {
      setDoiError(error.message);
    }
    setDoi("");
  };

  // 选择文件时切换右侧内容
  const handleSelectFile = (idx) => {
    setSelectedFileIndex(idx);
    setAbstractEntries({
      ...files[idx].meta,
      content: "",
    });
    fetch(`/api/notes?fileId=${files[idx].id}&username=${encodeURIComponent(username)}`) // ★加 username
      .then(res => res.json())
      .then(notesData => {
        setNotes(prevNotes => {
          const freeNotes = prevNotes.filter(n => n.type === "free");
          const otherNotes = (notesData || []).filter(n => n.type !== "free");
          return [...freeNotes, ...otherNotes];
        });
      });
  };

  const handleAddFreeNote = async () => {
    if (!freeNoteContent.trim()) return;
    const newNote = {
      id: "free-" + Date.now() + "-" + Math.random(),
      content: freeNoteContent,
      createdAt: new Date().toISOString(),
      type: "free"
    };
    setNotes(prev => [...prev, newNote]);
    setFreeNoteContent("");
    await fetch('/api/notes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...newNote, username }) // ★加 username
    });
  };

  const handleManualAddFile = async () => {
    if (!abstractEntries.title.trim()) return;
    const fileId = Date.now() + Math.random() + abstractEntries.title.replace(/[\/\\]/g, "_");
    const newNote = {
      id: Date.now() + Math.random(),
      fileId: fileId,
      content: abstractEntries.content,
      createdAt: new Date().toISOString()
    };
    const newFile = {
      id: fileId,
      title: abstractEntries.title,
      meta: { ...abstractEntries, type: "manual" },
      notes: [newNote]
    };
    await fetch('/api/files', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...newFile, username }) // ★加 username
    });
    await fetch('/api/notes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...newNote, username }) // ★加 username
    });
    setFiles(prev => {
      const updated = [...prev, newFile];
      setSelectedFileIndex(updated.length - 1);
      setAbstractEntries({
        ...newFile.meta,
        content: "",
      });
      setNotes([newNote]);
      return updated;
    });
  };

  // 生成APA格式引用
  function generateAPA(meta) {
    if (!meta) return '';
    return `${meta.author}. (${meta.date.slice(0, 10)}). ${meta.title}`;
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        width: "100%",
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        background: "#f5f5f5",
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
          padding: "32px 48px 0 48px",
          position: "relative",
          height: "120px", // 顶部栏高度可根据实际调整
          boxSizing: "border-box",
        }}
      >
        <Link href="/">
          <div
            style={{
              position: "absolute",
              top: "67px",
              left: "80px",
              fontWeight: "bold",
              fontSize: "24px",
              color: "#111",
            }}
          >
            <div style={{ fontSize: "32px", marginBottom: "8px" }}>NewZotero</div>
            <div style={{ fontSize: "18px", opacity: 0.8 }}>v0.1.22 知识库管理助手</div>
          </div>
        </Link>
        <div style={{ position: "absolute", top: "67px", right: "80px" }}>
          <button
            style={{
              background: "#111",
              color: "#fff",
              border: "none",
              borderRadius: "6px",
              padding: "12px 32px",
              fontSize: "24px",
              fontWeight: "bold",
              cursor: "default",
              marginRight: "24px",
            }}
            disabled={true}
          >
            笔记写入
          </button>
          <Link href="/notebrowse">
            <button
              className="search-btn"
            >
              笔记搜索
            </button>
          </Link>
        </div>
      </div>
      {/* 主体区域：上下平分 */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        {/* 上半部分 */}
        <div
          style={{
            background: "#fff",
            width: "100%",
            height: "50vh",
            minHeight: 0,
            display: "flex",
            flexDirection: "column",
            boxSizing: "border-box",
          }}
        >
          {/* 主体内容 */}
          <div
            style={{
              display: "flex",
              flex: 1,
              padding: "0 48px 0 48px",
              marginTop: "32px",
              gap: "32px",
              minHeight: 0,
            }}
          >
            {/* 左栏 */}
            <div style={{ flex: "0 0 480px", display: "flex", flexDirection: "column", gap: "12px", borderRight: "1px solid #E6E6E6", paddingRight: "24px" }}>
              <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                style={{
                  display: "flex",
                  flexDirection: "column",
                  border: "2px dashed #bbb",
                  borderRadius: "10px",
                  minHeight: "220px",
                  alignItems: "center",
                  justifyContent: "flex-start",
                  padding: "18px 0 0 0",
                  background: "#fafafa",
                  transition: "border-color 0.2s",
                  overflowY: "auto",
                  flex: "1 1 auto"
                }}
              >
                <button
                  style={{
                    background: "#111",
                    color: "#fff",
                    border: "none",
                    borderRadius: "6px",
                    padding: "18px 0",
                    fontSize: "20px",
                    fontWeight: "bold",
                    marginBottom: "18px",
                    cursor: "pointer",
                    width: "90%",
                  }}
                  onClick={() => fileInputRef.current.click()}
                >
                  导入文件
                </button>
                <div
                  onClick={() => {
                    setSelectedFileIndex("manual");
                    setAbstractEntries({
                      title: "",
                      author: "",
                      date: "",
                      page: "",
                      content: "",
                    });
                    setNotes([]);
                  }}
                  style={{
                    background: selectedFileIndex === "manual" ? "#e0eaff" : "#f5f5f5",
                    border: selectedFileIndex === "manual" ? "2px solid #1976d2" : "none",
                    borderRadius: "8px",
                    padding: "12px 16px",
                    marginBottom: "12px",
                    display: "flex",
                    alignItems: "center",
                    gap: "12px",
                    width: "90%",
                    cursor: "pointer",
                    position: "relative",
                  }}>
                  <Image src="/file_icon.svg" alt="icon" width={36} height={36} />
                  + 手动添加文件
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.docx,.doc"
                  multiple
                  style={{ display: "none" }}
                  onChange={handleFileChange}
                />
                {/* 文件列表 */}
                {files.length === 0 ? (
                  <div style={{ color: "#aaa", fontSize: "15px", marginTop: "40px" }}>
                    暂无文件
                  </div>
                ) : (
                  files.map((file, idx) => (
                    <div
                      key={file.title + idx}
                      onClick={() => handleSelectFile(idx)}
                      style={{
                        background: selectedFileIndex === idx ? "#e0eaff" : "#f5f5f5", // 高亮背景
                        border: selectedFileIndex === idx ? "2px solid #1976d2" : "none",
                        borderRadius: "8px",
                        padding: "12px 16px",
                        marginBottom: "12px",
                        display: "flex",
                        alignItems: "center",
                        gap: "12px",
                        width: "90%",
                        cursor: "pointer",
                        position: "relative",
                      }}
                    >
                      <Image src={getIcon(file.title)} alt="icon" width={36} height={36} />
                      <span style={{ fontSize: "15px", color: "#222", wordBreak: "break-all" }}>
                        {file.title}
                      </span>
                      <button
                        onClick={e => {
                          e.stopPropagation();
                          handleDelete(idx);
                        }}
                        style={{
                          position: "absolute",
                          right: "8px",
                          top: "50%",
                          transform: "translateY(-50%)",
                          background: "none",
                          border: "none",
                          color: "#d32f2f",
                          fontWeight: "bold",
                          fontSize: "18px",
                          cursor: "pointer",
                        }}
                        title="删除"
                      >
                        ×
                      </button>
                    </div>
                  ))
                )}
              </div>
              <div style={{ color: "#828282", fontSize: "18px", width: "90%" }}>
                使用说明：可以为每一个单体条文存储原始的文件（pdf或doc格式均可），单独记录摘要内容。<br />
                <br />
                推荐内容带有 “Free Writing” 一起保存
              </div>
            </div>
            {/* 右栏 */}

            <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "12px" }}>
              <div style={{ display: "flex", flexDirection: "column" }}>
                <div>
                  <span style={{ fontWeight: "bold", fontSize: "18px" }}>输入DOI</span>
                </div>
                <div>
                  <span style={{ color: "#7E7E7E", fontSize: "12px" }}>将自动导入该doi的所有信息（如有）</span>
                </div>
                <div>
                  <input
                    type="text"
                    value={doi}
                    onChange={(e) => setDoi(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        fetchDoiInfo();
                      }
                    }}
                    style={{
                      background: "#D9D9D9",
                      border: "none",
                      fontSize: "16px",
                      width: "100%",
                      boxSizing: "border-box",
                      padding: "6px 10px",
                    }} />
                </div>
                {doiError && <div style={{ color: "#d32f2f", fontSize: "12px" }}>{doiError}</div>}
              </div>
              <div style={{
                background: "#fafafa",
                padding: "6px 10px",
                fontSize: "16px",
                marginBottom: "8px",
                backgroundImage: `
                    linear-gradient(to right, #e0e0e0 1px, transparent 1px),
                    linear-gradient(to bottom, #e0e0e0 1px, transparent 1px)
                `,
                backgroundSize: "15px 15px",
              }}>
                <div style={{ display: "flex", alignItems: "center" }}>
                  <span style={{ fontSize: "22px", color: "#000", fontWeight: "bold" }}>(</span>
                  <input
                    type="text"
                    name="title"
                    value={abstractEntries.title}
                    placeholder="填写文章名"
                    onChange={handleEntryChange}
                    style={{
                      background: "none",
                      border: "none",
                      fontSize: "16px",
                      fontWeight: "bold",
                      color: "#8C8C8C",
                      outline: "none",
                      width: inputWidths.title,
                      minWidth: 40,
                      transition: "width 0.1s",
                      marginTop: "4px"
                    }}
                  />
                  <span
                    ref={titleSpan}
                    style={{
                      position: "absolute",
                      visibility: "hidden",
                      height: 0,
                      overflow: "hidden",
                      whiteSpace: "pre",
                      fontSize: "16px",
                      fontWeight: "bold",
                      fontFamily: "inherit",
                    }}
                  >
                    {abstractEntries.title || "填写文章名"}
                  </span>
                  <span style={{ fontSize: "22px", color: "#000", fontWeight: "bold" }}>)</span>
                </div>
                {/* 作者-日期-页码 */}
                <div style={{ display: "flex", alignItems: "center", fontSize: "15px", color: "#444" }}>
                  <span style={{ fontSize: "22px", color: "#000", fontWeight: "bold" }}>(</span>
                  <input
                    type="text"
                    name="author"
                    value={abstractEntries.author}
                    placeholder="填写作者"
                    onChange={handleEntryChange}
                    style={{
                      background: "none",
                      border: "none",
                      fontSize: "16px",
                      fontWeight: "bold",
                      color: "#8C8C8C",
                      outline: "none",
                      width: inputWidths.author,
                      minWidth: 40,
                      transition: "width 0.1s",
                      marginTop: "4px"
                    }}
                  />
                  <span
                    ref={authorSpan}
                    style={{
                      position: "absolute",
                      visibility: "hidden",
                      height: 0,
                      overflow: "hidden",
                      whiteSpace: "pre",
                      fontSize: "16px",
                      fontWeight: "bold",
                      fontFamily: "inherit",
                    }}
                  >
                    {abstractEntries.author || "填写作者"}
                  </span>
                  <span style={{ fontSize: "22px", color: "#000", fontWeight: "bold" }}>)</span>
                  <span style={{ fontSize: "22px", color: "#000", fontWeight: "bold", margin: "0 8px" }}>-</span>
                  <span style={{ fontSize: "22px", color: "#000", fontWeight: "bold" }}>(</span>
                  <input
                    type="text"
                    name="date"
                    value={abstractEntries.date}
                    placeholder="填写发表时间"
                    onChange={handleEntryChange}
                    style={{
                      background: "none",
                      border: "none",
                      fontSize: "16px",
                      fontWeight: "bold",
                      color: "#8C8C8C",
                      outline: "none",
                      width: inputWidths.date,
                      minWidth: 40,
                      transition: "width 0.1s",
                      marginTop: "4px"
                    }}
                  />
                  <span
                    ref={dateSpan}
                    style={{
                      position: "absolute",
                      visibility: "hidden",
                      height: 0,
                      overflow: "hidden",
                      whiteSpace: "pre",
                      fontSize: "16px",
                      fontWeight: "bold",
                      fontFamily: "inherit",
                    }}
                  >
                    {abstractEntries.date || "填写发表时间"}
                  </span>
                  <span style={{ fontSize: "22px", color: "#000", fontWeight: "bold" }}>)</span>
                  <span style={{ fontSize: "22px", color: "#000", fontWeight: "bold", margin: "0 8px" }}>-</span>
                  <span style={{ fontSize: "22px", color: "#000", fontWeight: "bold" }}>(</span>
                  <input
                    type="text"
                    name="page"
                    value={abstractEntries.page}
                    placeholder="填写引用页码，如无就没有"
                    onChange={handleEntryChange}
                    style={{
                      background: "none",
                      border: "none",
                      fontSize: "16px",
                      fontWeight: "bold",
                      color: "#8C8C8C",
                      outline: "none",
                      width: inputWidths.page,
                      minWidth: 40,
                      transition: "width 0.1s",
                      marginTop: "4px"
                    }}
                  />
                  <span
                    ref={pageSpan}
                    style={{
                      position: "absolute",
                      visibility: "hidden",
                      height: 0,
                      overflow: "hidden",
                      whiteSpace: "pre",
                      fontSize: "16px",
                      fontWeight: "bold",
                      fontFamily: "inherit",
                    }}
                  >
                    {abstractEntries.page || "填写引用页码，如无就没有"}
                  </span>
                  <span style={{ fontSize: "22px", color: "#000", fontWeight: "bold" }}>)</span>
                </div>
              </div>
              <div style={{
                background: "#fafafa",
                padding: "6px 10px",
                fontSize: "16px",
                marginBottom: "8px",
                backgroundImage: `
                    linear-gradient(to right, #e0e0e0 1px, transparent 1px),
                    linear-gradient(to bottom, #e0e0e0 1px, transparent 1px)
                `,
                display: "flex",
                justifyContent: "center",
                backgroundSize: "15px 15px",
                position: "relative",
              }}>
                <textarea
                  name="content"
                  onChange={handleEntryChange}
                  value={abstractEntries.content}
                  placeholder="（摘录内容粘贴在此）"
                  style={{
                    background: "none",
                    border: "none",
                    fontSize: "16px",
                    color: "#8C8C8C",
                    outline: "none",
                    width: "100%",
                    height: "80px",
                    resize: "none",
                    lineHeight: 1.5,
                    textAlign: "left",
                  }}
                  onKeyDown={e => {
                    if (e.ctrlKey && e.key === "Enter") {
                      if (selectedFileIndex === "manual") {
                        handleManualAddFile();
                      } else {
                        handleAddNote();
                      }
                    }
                  }}
                />
                <div style={{
                  position: "absolute",
                  right: "10px",
                  bottom: "10px",
                  fontSize: "12px",
                  color: "#888",
                }}>
                  回车换段 & Ctrl+Enter添加摘录
                </div>
              </div>
              <div
                className="hide-scrollbar"
                style={{
                  minHeight: "80px",
                  maxHeight: "320px",
                  marginBottom: "12px",
                  fontSize: "16px",
                  flex: 1,
                  overflowY: "auto",
                  overflowX: "auto",
                  background: "none",
                  border: "none",
                  padding: 0,
                }}
              >
                {notes.length === 0 && <div style={{ color: "#bbb" }}>暂无摘录</div>}
                {(noteExpanded ? notes.filter(n => n.type !== "free") : notes.filter(n => n.type !== "free").slice(0, 1)).map(note => (
                  <div
                    key={note.id}
                    style={{
                      marginBottom: 12,
                      border: "1px solid #e0e0e0",
                      padding: "12px 16px",
                      background: "#fafafa",
                      backgroundImage: `
                        linear-gradient(to right, #e0e0e0 1px, transparent 1px),
                        linear-gradient(to bottom, #e0e0e0 1px, transparent 1px)
                      `,
                      backgroundSize: "15px 15px",
                      display: "flex",
                      alignItems: "center",
                    }}
                  >
                    <div style={{ flex: 1, minWidth: 0, wordBreak: "break-all" }}>{note.content}</div>
                    <div style={{ color: "#888", fontSize: 12, marginLeft: 12, whiteSpace: "nowrap" }}>
                      {generateAPA(files[selectedFileIndex]?.meta)}
                    </div>
                    <button
                      style={{
                        color: "#d32f2f",
                        border: "none",
                        background: "none",
                        cursor: "pointer",
                        fontSize: 12,
                        marginLeft: 12,
                      }}
                      onClick={() => handleDeleteNote(note.id)}
                    >
                      删除
                    </button>
                  </div>
                ))}
                {notes.length > 1 && (
                  <div style={{ textAlign: "center", marginTop: 8 }}>
                    <button
                      style={{ border: "none", background: "none", color: "#000", cursor: "pointer", fontSize: 14 }}
                      onClick={() => setNoteExpanded(e => !e)}
                    >
                      {noteExpanded ? "收起" : "展开"}
                      <span style={{ marginLeft: 4 }}>{noteExpanded ? "▲" : "▼"}</span>
                    </button>
                  </div>
                )}
              </div>
            </div>

          </div>
        </div>
        {/* 下半部分：自由笔记区 */}
        <div
          style={{
            background: "#cccccc",
            width: "100%",
            flex: 1,
            minHeight: 0,
            boxSizing: "border-box",
            padding: "0 0 0 0",
            overflow: "auto",
          }}
        >
          <div
            style={{
              display: "flex",
              flex: 1,
              padding: "32px 48px",
              gap: "32px",
              minHeight: 0,
            }}
          >
            {/* 左栏：标题和说明 */}
            <div style={{ flex: "0 0 480px", display: "flex", flexDirection: "column", gap: "12px", paddingRight: "24px" }}>
              <div style={{ fontWeight: "normal", fontSize: "24px", marginBottom: "12px" }}>
                自由笔记区<br />
                <span style={{ fontWeight: "normal", fontSize: "24px", marginTop: "12px" }}>"Free Writing Zone"</span>
              </div>
              <div style={{ color: "#828282", fontSize: "15px", marginBottom: "18px" }}>
                自由写作是一种在规定时间内连续写作的技巧，无需担心语法、拼写或结构，以产生想法并克服写作障碍这 是一种让您的思绪自由流淌在纸上的方式，帮助您探索主题、发现新想法并突破创造性障碍。<br />
                <br />
                ——边记录文献，边记录想法吧！
              </div>
            </div>
            {/* 右栏：自由笔记内容 */}
            <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "12px" }}>
              {/* 示例自由笔记 */}
              <div style={{
                background: "#cccccc",
                padding: "6px 10px",
                fontSize: "16px",
                marginBottom: "8px",
                backgroundImage: `
                  linear-gradient(to right, #a0a0a0 1px, transparent 1px),
                  linear-gradient(to bottom, #a0a0a0 1px, transparent 1px)
                `,
                display: "flex",
                justifyContent: "center",
                backgroundSize: "15px 15px",
                position: "relative",
              }}>
                <textarea
                  className="black-placeholder"
                  value={freeNoteContent}
                  onChange={(e) => setFreeNoteContent(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.ctrlKey && e.key === "Enter") handleAddFreeNote();
                  }}
                  placeholder="（写入你的碎片想法）"
                  style={{
                    background: "none",
                    border: "none",
                    fontSize: "16px",
                    color: "#000000",
                    outline: "none",
                    width: "100%",
                    height: "80px",
                    resize: "none",
                    lineHeight: 1.5,
                    textAlign: "left",
                    marginTop: "10px",
                  }}
                />
              </div>
              {/* 自由笔记展示区 */}
              <div
                className="hide-scrollbar"
                style={{
                  minHeight: "80px",
                  maxHeight: "320px",
                  marginBottom: "12px",
                  fontSize: "16px",
                  flex: 1,
                  overflowY: "auto",
                  overflowX: "auto",
                  background: "none",
                  border: "none",
                  padding: 0,
                }}
              >
                {notes.filter(n => n.type === "free").length === 0 && (
                  <div style={{ color: "#828282" }}>暂无自由笔记</div>
                )}
                {notes.filter(n => n.type === "free").map(note => (
                  <div
                    key={note.id}
                    style={{
                      marginBottom: 12,
                      border: "1px solid #e0e0e0",
                      padding: "12px 16px",
                      background: "#cccccc",
                      backgroundImage: `
                        linear-gradient(to right, #a0a0a0 1px, transparent 1px),
                        linear-gradient(to bottom, #a0a0a0 1px, transparent 1px)
                      `,
                      backgroundSize: "15px 15px",
                      display: "flex",
                      alignItems: "center",
                    }}
                  >
                    <div style={{ flex: 1, minWidth: 0, wordBreak: "break-all", position: "relative" }}>
                      <div style={{
                        position: "absolute",
                        top: 0,
                        left: 0,
                        fontSize: "24px",
                        color: "#000",
                        fontWeight: "bold",
                        padding: "0 0 4px 0",
                        background: "transparent",
                        lineHeight: 1.2,
                        zIndex: 1
                      }}>
                        （{note.createdAt.slice(0, 10)}）
                      </div>
                      <div style={{ paddingTop: "32px", fontSize: "16px", color: "#000" }}>
                        {note.content}
                      </div>
                    </div>
                    <button
                      style={{
                        color: "#d32f2f",
                        border: "none",
                        background: "none",
                        cursor: "pointer",
                        fontSize: 12,
                        marginLeft: 12,
                      }}
                      onClick={() => handleDeleteNote(note.id)}
                    >
                      删除
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div >
  );
}