'use client';

import Image from "next/image";
import Link from "next/link";
import { useState } from "react";

export default function HomePage() {
  const [feedback, setFeedback] = useState({
    email: "",
    context: "",
  });
  const [submitted, setSubmitted] = useState(false);
  const [submitResult, setSubmitResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    // 判断内容是否为空
    // if (feedback.email.trim() && feedback.context.trim()) {
    //   setSubmitted(true);
    //   setTimeout(() => {
    //     setSubmitted(false);
    //     setFeedback({ email: "", context: "" });
    //   }, 3000);
    // }
    setSubmitted(true);
    setSubmitResult(null);

    try{
      const res = await fetch('/api/send-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(feedback),
      });
      const result = await res.json();
      if (res.ok) {
          setSubmitResult({
            type: "success",
            message: result.message || "反馈已提交，我们将尽快回复您！",
          });
          setFeedback({ email: "", context: "" });
        } else {
          setSubmitResult({
            type: "error",
            message: result.error || "提交失败，请稍后再试",
            details: result.details,
          });
        }
      } catch (error) {
        setSubmitResult({
          type: "error",
          message: "网络错误，请检查您的连接",
          details: error.message,
        });
      } finally {
        setSubmitted(false);
      }

  };

  const handleChange = (e) => {
    setFeedback({ ...feedback, [e.target.name]: e.target.value });
  }
  return (
    <div
      style={{
        minHeight: "100vh",
        width: "100%",
        background: "#000",
        position: "relative",
        overflow: "hidden",
        margin: 0,
        padding: 0,
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
      }}
    >
      {/* 背景装饰元素 */}
      <div
        style={{
          position: "absolute",
          top: "10%",
          left: "5%",
          width: "300px",
          height: "300px",
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(25, 118, 210, 0.2) 0%, transparent 70%)",
          zIndex: 0,
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: "15%",
          right: "5%",
          width: "400px",
          height: "400px",
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(76, 175, 80, 0.15) 0%, transparent 70%)",
          zIndex: 0,
        }}
      />

      {/* 主内容区域 */}
      <div
        style={{
          position: "relative",
          height: "calc(100vh - 400px)",
          width: "100%",
          boxSizing: "border-box",
          zIndex: 1,
          paddingBottom: 0,
          overflow: "hidden",
        }}
      >
        {/* 标题和版本信息 */}
        <div
          style={{
            position: "absolute",
            top: "67px",
            left: "80px",
            color: "#fff",
            fontSize: "24px",
            fontWeight: "bold",
            zIndex: 1,
          }}
        >
          <div style={{ fontSize: "32px", marginBottom: "8px" }}>NewZotero</div>
          <div style={{ fontSize: "18px", opacity: 0.8 }}>v1.22 知识库管理助手</div>
        </div>

        {/* 主标题区域 */}
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "10%",
            transform: "translateY(-50%)",
            color: "#fff",
            maxWidth: "700px",
            zIndex: 1,
          }}
        >
          <div
            style={{
              fontSize: "clamp(36px, 6vw, 64px)",
              fontWeight: "bold",
              lineHeight: "1.1",
              marginBottom: "20px",
            }}
          >
            Empower your next Academic Journey With AI
          </div>
          <div
            style={{
              fontSize: "clamp(16px, 2vw, 20px)",
              opacity: 0.9,
              lineHeight: "1.6",
              maxWidth: "600px",
            }}
          >
            革命性的知识管理工具，结合人工智能技术，帮助研究人员高效整理、分析和应用学术资源。
          </div>
        </div>

        {/* 进入知识库按钮 */}
        <Link href="/login" style={{ textDecoration: "none" }}>
          <button
            style={{
              position: "absolute",
              top: "40px",
              right: "40px",
              background: "rgba(255, 255, 255, 0.2)",
              color: "#fff",
              border: "1px solid rgba(255, 255, 255, 0.2)",
              borderRadius: "8px",
              padding: "12px 24px",
              fontSize: "16px",
              fontWeight: 500,
              cursor: "pointer",
              zIndex: 1,
              backdropFilter: "blur(10px)",
              transition: "all 0.3s ease",
            }}
            onMouseEnter={(e) => {
              e.target.style.background = "rgba(255, 255, 255, 0.2)";
              e.target.style.transform = "translateX(5px)";
            }}
            onMouseLeave={(e) => {
              e.target.style.background = "rgba(255, 255, 255, 0.1)";
              e.target.style.transform = "translateX(0)";
            }}
          >
            进入个人知识库
          </button>
        </Link>

        {/* Get Started按钮 */}
        <Link href="/login" style={{ textDecoration: "none" }}>
          <button
            style={{
              position: "absolute",
              bottom: "40px",
              right: "40px",
              background: "rgba(255, 255, 255, 0.2)",
              color: "#fff",
              border: "1px solid rgba(255, 255, 255, 0.2)",
              borderRadius: "8px",
              padding: "16px 40px",
              fontSize: "18px",
              fontWeight: "bold",
              cursor: "pointer",
              zIndex: 1,
              display: "flex",
              alignItems: "center",
              gap: "8px",
              transition: "all 0.3s ease",
            }}
            onMouseEnter={(e) => {
              e.target.style.background = "rgba(255, 255, 255, 0.2)";
              e.target.style.transform = "translateX(5px)";
            }}
            onMouseLeave={(e) => {
              e.target.style.background ="rgba(255, 255, 255, 0.2)";
              e.target.style.transform = "translateX(0)";
            }}
          >
            Get Started
            <span style={{ fontSize: "24px" }}>→</span>
          </button>
        </Link>
      </div>

      {/* 底部反馈区域 */}
      <div
        style={{
          position: "fixed",
          left: 0,
          bottom: 0,
          width: "100%",
          height: "350px",
          background: "rgba(255, 255, 255, 0.95)",
          boxSizing: "border-box",
          zIndex: 2,
          boxShadow: "0 -4px 20px rgba(0, 0, 0, 0.1)",
        }}
      >
        <div
          style={{
            maxWidth: "80%",
            margin: "0 auto",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <div
            style={{
              fontWeight: "bold",
              fontSize: "22px",
              marginTop: "15px",
              color: "#222",
            }}
          >
            任何建议和问题？
          </div>
          <div
            style={{
              marginBottom: "20px",
              color: "#444",
              fontSize: "16px",
              lineHeight: "1.6",
            }}
          >
            在这里留下你的邮箱和建议或提问，我们会在24小时内邮箱回复！
          </div>

          <form
            onSubmit={handleSubmit}
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "12px",
              maxWidth: "80%",
            }}
          >
            <input
              type="email"
              name="email"
              value={feedback.email}
              onChange={handleChange}
              placeholder="请输入您的邮箱"
              style={{
                padding: "12px 16px",
                borderRadius: "8px",
                border: "1px solid #ddd",
                fontSize: "16px",
                width: "100%",
                boxSizing: "border-box",
              }}
              required
            />
            <textarea
              name="context"
              value={feedback.context}
              onChange={handleChange}
              placeholder="请输入您的建议或问题"
              style={{
                padding: "12px 16px",
                borderRadius: "8px",
                border: "1px solid #ddd",
                fontSize: "16px",
                width: "100%",
                minHeight: "60px",
                boxSizing: "border-box",
                resize: "vertical",
              }}
              required
            />
            <button
              type="submit"
              style={{
                background: "#000",
                color: "#fff",
                border: "none",
                borderRadius: "8px",
                padding: "12px 24px",
                fontSize: "16px",
                fontWeight: "bold",
                cursor: "pointer",
                width: "120px",
                transition: "background 0.3s ease",
              }}
            >
              {submitted ? "提交中..." : "提交反馈"}
            </button>
          </form>

          {submitResult && (
            <div
              style={{
                marginTop: "16px",
                padding: "10px",
                background: "#4caf50",
                color: "white",
                borderRadius: "6px",
                maxWidth: "600px",
              }}
            >
              {submitResult.message}
              {submitResult.details && (
                <div style={{ fontSize: "14px", marginTop: "8px" }}>
                  详情: {submitResult.details}
                </div>
              )}
            </div>
          )}

          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-end",
              marginTop: "24px",
              color: "#666",
              fontSize: "14px",
              flexWrap: "wrap",
              gap: "16px",
            }}
          >
            <div>
              <div>当前为试用版</div>
              <div>感谢Raymond Zhang，Alfred Wang</div>
            </div>
            <div style={{ textAlign: "right" }}>
              <div>© 2025 NewZotero 知识库管理助手</div>
              <div>学术研究 AI 驱动解决方案</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}