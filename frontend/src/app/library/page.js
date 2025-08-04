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
  const [noteExpandedMap, setNoteExpandedMap] = useState({});
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

    // 首先加载自由笔记（无论是否有文件）
    fetch(`/api/notes?username=${encodeURIComponent(username)}`)
      .then(res => res.json())
      .then(allNotes => {
        const freeNotes = (allNotes || []).filter(n => n.type === "free");
        setNotes(freeNotes); // 先设置自由笔记

        // 然后加载文件和对应的摘录笔记
        return fetch(`/api/files?username=${encodeURIComponent(username)}`)
          .then((res) => res.json())
          .then((data) => {
            setFiles(data || []);
            if (data.length > 0) {
              setSelectedFileIndex(0);
              setAbstractEntries({
                ...data[0].meta,
                content: "",
              });
              // 加载第一个文件的摘录笔记
              return fetch(`/api/notes?fileId=${data[0].id}&username=${encodeURIComponent(username)}`)
                .then(res => res.json())
                .then(fileNotes => {
                  const abstractNotes = (fileNotes || []).filter(n => n.type !== "free");
                  setNotes(prevNotes => [...prevNotes, ...abstractNotes]); // 合并自由笔记和摘录笔记
                });
            }
          });
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

    // 先清空输入框
    const originalContent = abstractEntries.content;
    setAbstractEntries({ ...abstractEntries, content: "" });

    try {
      // 1. 同步到后端
      const response = await fetch('/api/notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...newNote, username })
      });

      if (!response.ok) {
        throw new Error(`后端保存失败: ${response.status}`);
      }

      // 2. 后端成功后再更新本地状态
      setNotes(prev => [...prev, newNote]);

    } catch (error) {
      console.error('保存笔记失败:', error);
      // 恢复输入框内容
      setAbstractEntries({ ...abstractEntries, content: originalContent });
      // 可以在这里添加用户提示
    }
  };

  // 删除摘录
  const handleDeleteNote = async (noteId) => {
    // 先获取要删除的笔记，以便失败时恢复
    const noteToDelete = notes.find(n => n.id === noteId);
    if (!noteToDelete) return;

    try {
      // 1. 先从UI中移除
      setNotes(prev => prev.filter(n => n.id !== noteId));

      // 2. 同步到后端
      const response = await fetch('/api/notes', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: noteId, username })
      });

      if (!response.ok) {
        throw new Error(`删除失败: ${response.status}`);
      }

    } catch (error) {
      console.error('删除笔记失败:', error);
      // 恢复删除的笔记
      setNotes(prev => [...prev, noteToDelete]);
      // 可以在这里添加用户提示
    }
  };

  // 拖拽上传
  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();

    const droppedFiles = Array.from(e.dataTransfer.files).filter(
      (file) =>
        file.name.toLowerCase().endsWith(".pdf") ||
        file.name.toLowerCase().endsWith(".docx") ||
        file.name.toLowerCase().endsWith(".doc")
    );

    if (droppedFiles.length === 0) {
      alert("请拖拽 PDF 或 Word 文档文件");
      return;
    }

    for (const file of droppedFiles) {
      try {
        // 创建 FormData 对象
        const formData = new FormData();
        formData.append('file', file);
        formData.append('username', username);

        // 调用前端API上传文件
        const response = await fetch('/api/upload', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          const error = await response.json();
          alert(`上传失败: ${error.error || '未知错误'}`);
          continue;
        }

        const result = await response.json();

        // 重新加载文件列表
        const filesResponse = await fetch(`/api/files?username=${encodeURIComponent(username)}`);
        const updatedFiles = await filesResponse.json();
        setFiles(updatedFiles || []);

        // 选中新上传的文件
        const newFileIndex = updatedFiles.findIndex(f => f.id === result.fileId);
        if (newFileIndex >= 0) {
          setSelectedFileIndex(newFileIndex);
          setAbstractEntries({
            ...updatedFiles[newFileIndex].meta,
            content: "",
          });
          setNotes(prevNotes => prevNotes.filter(n => n.type === "free"));
        }

        alert(`文件 "${file.name}" 上传成功！`);
      } catch (error) {
        console.error('上传文件时出错:', error);
        alert(`上传文件 "${file.name}" 失败，请重试`);
      }
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  // 点击上传
  const handleFileChange = async (e) => {
    const selectedFiles = Array.from(e.target.files).filter(
      (file) =>
        file.name.toLowerCase().endsWith(".pdf") ||
        file.name.toLowerCase().endsWith(".docx") ||
        file.name.toLowerCase().endsWith(".doc")
    );

    if (selectedFiles.length === 0) {
      alert("请选择 PDF 或 Word 文档文件");
      return;
    }

    for (const file of selectedFiles) {
      try {
        // 创建 FormData 对象
        const formData = new FormData();
        formData.append('file', file);
        formData.append('username', username);

        // 调用前端API上传文件
        const response = await fetch('/api/upload', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          const error = await response.json();
          alert(`上传失败: ${error.error || '未知错误'}`);
          continue;
        }

        const result = await response.json();

        // 重新加载文件列表
        const filesResponse = await fetch(`/api/files?username=${encodeURIComponent(username)}`);
        const updatedFiles = await filesResponse.json();
        setFiles(updatedFiles || []);

        // 选中新上传的文件
        const newFileIndex = updatedFiles.findIndex(f => f.id === result.fileId);
        if (newFileIndex >= 0) {
          setSelectedFileIndex(newFileIndex);
          setAbstractEntries({
            ...updatedFiles[newFileIndex].meta,
            content: "",
          });
          setNotes(prevNotes => prevNotes.filter(n => n.type === "free"));
        }

        alert(`文件 "${file.name}" 上传成功！`);
      } catch (error) {
        console.error('上传文件时出错:', error);
        alert(`上传文件 "${file.name}" 失败，请重试`);
      }
    }

    e.target.value = "";
  };


  // 删除文件
  const handleDelete = async (idx) => {
    const fileToDelete = files[idx];

    try {
      // 对于已上传的文件，使用新的删除API
      if (fileToDelete.meta && fileToDelete.meta.downloadable) {
        const response = await fetch(`/api/files/delete/${fileToDelete.id}?username=${encodeURIComponent(username)}`, {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) {
          const error = await response.json();
          alert(`删除失败: ${error.error || '未知错误'}`);
          return;
        }
      } else {
        // 对于其他文件，使用原有的删除逻辑
        await fetch('/api/files', {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id: fileToDelete.id, username })
        });
      }

      // 删除该文件的所有notes
      await fetch('/api/notes', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fileId: fileToDelete.id, username })
      });

      // 本地更新
      const newFiles = files.filter((_, i) => i !== idx);
      setFiles(newFiles);

      // 如果还有文件，切换到第一个文件并加载其notes
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
    } catch (error) {
      console.error('删除文件时出错:', error);
      alert('删除文件失败，请重试');
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
    setNoteExpanded(false);

    // 重新加载所有笔记，确保自由笔记和该文件的摘录笔记都显示
    fetch(`/api/notes?username=${encodeURIComponent(username)}`)
      .then(res => res.json())
      .then(allNotes => {
        const freeNotes = (allNotes || []).filter(n => n.type === "free");

        // 加载该文件的摘录笔记
        return fetch(`/api/notes?fileId=${files[idx].id}&username=${encodeURIComponent(username)}`)
          .then(res => res.json())
          .then(fileNotes => {
            const abstractNotes = (fileNotes || []).filter(n => n.type !== "free");
            setNotes([...freeNotes, ...abstractNotes]);
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

    // 先清空输入框
    const originalContent = freeNoteContent;
    setFreeNoteContent("");

    try {
      // 1. 同步到后端
      const response = await fetch('/api/notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...newNote, username })
      });

      if (!response.ok) {
        throw new Error(`后端保存失败: ${response.status}`);
      }

      // 2. 后端成功后再更新本地状态
      setNotes(prev => [...prev, newNote]);

    } catch (error) {
      console.error('保存自由笔记失败:', error);
      // 恢复输入框内容
      setFreeNoteContent(originalContent);
      // 可以在这里添加用户提示
    }
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
      // 保持自由笔记，只添加新的摘录笔记
      setNotes(prevNotes => {
        const freeNotes = prevNotes.filter(n => n.type === "free");
        return [...freeNotes, newNote];
      });
      return updated;
    });
  };

  // 生成APA格式引用
  function generateAPA(meta) {
    if (!meta) return '';
    return `${meta.author}. (${meta.date.slice(0, 10)}). ${meta.title}`;
  }

  const currentFileId = files[selectedFileIndex]?.id;
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
      <div style={{ flex: 1, display: "flex", flexDirection: "column", overflowX: "hidden" }}>
        {/* 上半部分 */}
        <div
          style={{
            background: "#fff",
            width: "100%",
            height: "50vh",
            minHeight: "400px",
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
              padding: "0 3vw",
              marginTop: "2vh",
              gap: "2vw",
              minHeight: 0,
            }}
          >
            {/* 左栏 */}
            <div style={{ flex: "0 0 30vw", maxWidth: "480px", minWidth: "300px", display: "flex", flexDirection: "column", gap: "1vh", borderRight: "1px solid #E6E6E6", paddingRight: "1.5vw" }}>
              <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                style={{
                  display: "flex",
                  flexDirection: "column",
                  border: "2px dashed #bbb",
                  borderRadius: "10px",
                  minHeight: "25vh",
                  alignItems: "center",
                  justifyContent: "flex-start",
                  padding: "1.5vh 0 0 0",
                  background: "#fafafa",
                  transition: "border-color 0.2s",
                  flex: "1 1 auto"
                }}
              >
                <button
                  style={{
                    background: "#111",
                    color: "#fff",
                    border: "none",
                    borderRadius: "6px",
                    padding: "1.5vh 0",
                    fontSize: "clamp(16px, 1.8vw, 20px)",
                    fontWeight: "bold",
                    marginBottom: "1.5vh",
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
                    setNotes(prevNotes => prevNotes.filter(n => n.type === "free"));
                  }}
                  style={{
                    background: selectedFileIndex === "manual" ? "#e0eaff" : "#f5f5f5",
                    border: selectedFileIndex === "manual" ? "2px solid #1976d2" : "none",
                    borderRadius: "8px",
                    padding: "1vh 1vw",
                    marginBottom: "1vh",
                    display: "flex",
                    alignItems: "center",
                    gap: "0.8vw",
                    width: "80%",
                    cursor: "pointer",
                    position: "relative",
                    fontSize: "clamp(12px, 1.2vw, 16px)",
                  }}>
                  <Image src="/file_icon.svg" alt="icon" width={32} height={32} />
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
                  <div style={{ color: "#aaa", fontSize: "clamp(12px, 1.2vw, 15px)", marginTop: "3vh" }}>
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
                        padding: "1vh 1vw",
                        marginBottom: "1vh",
                        display: "flex",
                        alignItems: "center",
                        gap: "0.8vw",
                        width: "80%",
                        cursor: "pointer",
                        position: "relative",
                      }}
                    >
                      <Image src={getIcon(file.title)} alt="icon" width={32} height={32} />
                      <span style={{ fontSize: "clamp(12px, 1.2vw, 15px)", color: "#222", wordBreak: "break-all", flex: 1 }}>
                        {file.title}
                      </span>
                      <button
                        onClick={e => {
                          e.stopPropagation();
                          handleDelete(idx);
                        }}
                        style={{
                          position: "absolute",
                          right: "0.5vw",
                          top: "50%",
                          transform: "translateY(-50%)",
                          background: "none",
                          border: "none",
                          color: "#d32f2f",
                          fontWeight: "bold",
                          fontSize: "clamp(14px, 1.5vw, 18px)",
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
              <div style={{ color: "#828282", fontSize: "clamp(12px, 1.4vw, 18px)", width: "90%" }}>
                使用说明：可以为每一个你想保存或摘录的文献（pdf或docs格式均可）单独记录摘录内容。<br />
                <br />
                推荐内容带有 “Free Writing” 一起保存
              </div>
            </div>
            {/* 右栏 */}

            <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "1vh" }}>
              <div style={{ display: "flex", flexDirection: "column" }}>
                <div>
                  <span style={{ fontWeight: "bold", fontSize: "clamp(14px, 1.6vw, 18px)" }}>输入DOI</span>
                </div>
                <div>
                  <span style={{ color: "#7E7E7E", fontSize: "clamp(10px, 1vw, 12px)" }}>将自动导入该doi的所有信息（如有）</span>
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
                      fontSize: "clamp(14px, 1.4vw, 16px)",
                      width: "100%",
                      boxSizing: "border-box",
                      padding: "0.5vh 1vw",
                    }} />
                </div>
                {doiError && <div style={{ color: "#d32f2f", fontSize: "clamp(10px, 1vw, 12px)" }}>{doiError}</div>}
              </div>
              <div style={{
                background: "#fafafa",
                padding: "0.5vh 1vw",
                fontSize: "clamp(14px, 1.4vw, 16px)",
                marginBottom: "1vh",
                backgroundImage: `
                    linear-gradient(to right, #e0e0e0 1px, transparent 1px),
                    linear-gradient(to bottom, #e0e0e0 1px, transparent 1px)
                `,
                backgroundSize: "15px 15px",
              }}>
                <div style={{ display: "flex", alignItems: "center" }}>
                  <span style={{ fontSize: "clamp(18px, 2vw, 22px)", color: "#000", fontWeight: "bold" }}>(</span>
                  <input
                    type="text"
                    name="title"
                    value={abstractEntries.title}
                    placeholder="填写文章名"
                    onChange={handleEntryChange}
                    style={{
                      background: "none",
                      border: "none",
                      fontSize: "clamp(14px, 1.4vw, 16px)",
                      fontWeight: "bold",
                      color: "#8C8C8C",
                      outline: "none",
                      width: inputWidths.title,
                      minWidth: 40,
                      transition: "width 0.1s",
                      marginTop: "0.3vh"
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
                      fontSize: "clamp(14px, 1.4vw, 16px)",
                      fontWeight: "bold",
                      fontFamily: "inherit",
                    }}
                  >
                    {abstractEntries.title || "填写文章名"}
                  </span>
                  <span style={{ fontSize: "clamp(18px, 2vw, 22px)", color: "#000", fontWeight: "bold" }}>)</span>
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
                      fontSize: "clamp(14px, 1.4vw, 16px)",
                      fontWeight: "bold",
                      color: "#8C8C8C",
                      outline: "none",
                      width: inputWidths.author,
                      minWidth: 40,
                      transition: "width 0.1s",
                      marginTop: "0.3vh"
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
                      fontSize: "clamp(14px, 1.4vw, 16px)",
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
                padding: "0.5vh 1vw",
                fontSize: "clamp(14px, 1.4vw, 16px)",
                marginBottom: "1vh",
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
                    fontSize: "clamp(14px, 1.4vw, 16px)",
                    color: "#8C8C8C",
                    outline: "none",
                    width: "100%",
                    height: "8vh",
                    minHeight: "60px",
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
                  right: "1vw",
                  bottom: "0.5vh",
                  fontSize: "clamp(10px, 1vw, 12px)",
                  color: "#888",
                }}>
                  回车换段 & Ctrl+Enter添加摘录
                </div>
              </div>
              <div
                className="hide-scrollbar"
                style={{
                  minHeight: "8vh",
                  maxHeight: "35vh",
                  marginBottom: "1vh",
                  fontSize: "clamp(14px, 1.4vw, 16px)",
                  flex: 1,
                  overflowY: "auto",
                  overflowX: "auto",
                  background: "none",
                  border: "none",
                  padding: 0,
                }}
              >
                {notes.filter(n => n.type !== "free" && n.fileId === currentFileId).length === 0 && <div style={{ color: "#bbb" }}>暂无摘录</div>}
                {(noteExpandedMap[currentFileId] !== false  // 默认展开，除非显式设置为false
                  ? notes.filter(n => n.type !== "free" && n.fileId === currentFileId)  // 只显示当前文件的摘录笔记
                  : notes.filter(n => n.type !== "free" && n.fileId === currentFileId).slice(0, 1)
                ).map(note => (
                  <div
                    key={note.id}
                    className="abstract-note"
                  >
                    <div className="abstract-note-content">{note.content}</div>
                    <div className="abstract-note-footer">
                      <div className="abstract-note-apa">
                        {generateAPA(files[selectedFileIndex]?.meta)}
                      </div>
                      <button
                        className="abstract-note-delete"
                        onClick={() => handleDeleteNote(note.id)}
                      >
                        删除
                      </button>
                    </div>
                  </div>
                ))}
                {notes.filter(n => n.type !== "free" && n.fileId === currentFileId).length > 1 && (
                  <div style={{ textAlign: "center", marginTop: "1vh" }}>
                    <button
                      style={{ border: "none", background: "none", color: "#000", cursor: "pointer", fontSize: "clamp(12px, 1.2vw, 14px)" }}
                      onClick={() => setNoteExpandedMap(map => ({
                        ...map,
                        [currentFileId]: map[currentFileId] === false ? true : false  // 切换状态
                      }))}
                    >
                      {noteExpandedMap[currentFileId] !== false ? "收起" : "展开"}
                      <span style={{ marginLeft: "0.5vw" }}>{noteExpandedMap[currentFileId] !== false ? "▲" : "▼"}</span>
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
              padding: "2vh 3vw",
              gap: "2vw",
              minHeight: 0,
            }}
          >
            {/* 左栏：标题和说明 */}
            <div style={{ flex: "0 0 30vw", maxWidth: "480px", minWidth: "300px", display: "flex", flexDirection: "column", gap: "1vh", paddingRight: "1.5vw" }}>
              <div style={{ fontWeight: "normal", fontSize: "clamp(18px, 2.2vw, 24px)", marginBottom: "1vh" }}>
                自由笔记区<br />
                <span style={{ fontWeight: "normal", fontSize: "clamp(18px, 2.2vw, 24px)", marginTop: "1vh" }}>"Free Writing Zone"</span>
              </div>
              <div style={{ color: "#828282", fontSize: "clamp(12px, 1.2vw, 15px)", marginBottom: "1.5vh" }}>
                自由写作是一种在规定时间内连续写作的技巧，无需担心语法、拼写或结构，以产生想法并克服写作障碍这 是一种让您的思绪自由流淌在纸上的方式，帮助您探索主题、发现新想法并突破创造性障碍。<br />
                <br />
                ——边记录文献，边记录想法吧！
              </div>
            </div>
            {/* 右栏：自由笔记内容 */}
            <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "1vh" }}>
              {/* 示例自由笔记 */}
              <div style={{
                background: "#cccccc",
                padding: "0.5vh 1vw",
                fontSize: "clamp(14px, 1.4vw, 16px)",
                marginBottom: "1vh",
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
                    fontSize: "clamp(14px, 1.4vw, 16px)",
                    color: "#000000",
                    outline: "none",
                    width: "100%",
                    height: "8vh",
                    minHeight: "60px",
                    resize: "none",
                    lineHeight: 1.5,
                    textAlign: "left",
                    marginTop: "1vh",
                  }}
                />
              </div>
              {/* 自由笔记展示区 */}
              <div
                className="hide-scrollbar"
                style={{
                  minHeight: "8vh",
                  maxHeight: "35vh",
                  marginBottom: "1vh",
                  fontSize: "clamp(14px, 1.4vw, 16px)",
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
                      marginBottom: "1vh",
                      border: "1px solid #e0e0e0",
                      padding: "1vh 1vw",
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
                        fontSize: "clamp(18px, 2vw, 24px)",
                        color: "#000",
                        fontWeight: "bold",
                        padding: "0 0 4px 0",
                        background: "transparent",
                        lineHeight: 1.2,
                        zIndex: 1
                      }}>
                        （{note.createdAt.slice(0, 10)}）
                      </div>
                      <div style={{ paddingTop: "2.5vh", fontSize: "clamp(14px, 1.4vw, 16px)", color: "#000" }}>
                        {note.content}
                      </div>
                    </div>
                    <button
                      style={{
                        color: "#d32f2f",
                        border: "none",
                        background: "none",
                        cursor: "pointer",
                        fontSize: "clamp(10px, 1vw, 12px)",
                        marginLeft: "1vw",
                        flexShrink: 0,
                        padding: "0.2vh 0.5vw",
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