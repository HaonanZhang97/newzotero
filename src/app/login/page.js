'use client';
import Image from "next/image";
import Link from "next/link";
import { useState, useEffect } from "react";


export default function LoginPage() {

  const [userID, setUserID] = useState("");
  const [checkResult, setCheckResult] = useState("");
  const [foundError, setfoundError] = useState(false);

  useEffect(() => {
    if (!userID) {
      setCheckResult("未使用过的ID将建立新数据库");
      setfoundError(false);
      return;
    }
    if (foundError) {
      setCheckResult("检查ID时出错，请稍后再试");
      return;
    }

    let ignore = false;
    setCheckResult("🔍 正在检测用户...");
    const checkUser = async () => {
      try {
        const formData = new FormData();
        formData.append("username", userID);
        const response = await fetch("/api/check_user", {
          method: "POST",
          body: formData,
        });
        if (!response.ok) {
          throw new Error("网络错误，请稍后再试");
        }
        const data = await response.json();
        if (ignore) return;
        if (data.exists) {
          setCheckResult("✅ 用户数据已存在，可以继续使用");
        } else {
          setCheckResult("📂 首次使用，请创建自己的知识库");
        }
      } catch (error) {
        if (!ignore) setCheckResult("检查ID时出错，请稍后再试");
        setfoundError(true);
      } 
    };
    checkUser();
    return () => { ignore = true; };
  }, [userID]);


  return (
    <div
      style={{
        minHeight: "100vh",
        width: "100%",
        background: "#fff",
        position: "relative",
        overflow: "hidden",
        margin: 0,
        padding: 0,
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
      }}
    >
      {/* 顶部标题 */}
      <Link href= "/"> 
        <div
          href="/"
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
      {/* 主体区域 */}
      <div
        style={{
          display: "flex",
          width: "100%",
          marginTop: "8%",
        }}
      >
        {/* 左侧图片 */}
        <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <Image
            src="/ChatGPT_Image_2025726_14_00_47.png"
            alt="ChatGPT Tree"
            width={700}
            height={950}
            style={{
              background: "#fafafa",
              boxShadow: "0 2px 16px rgba(0,0,0,0.04)",
              objectFit: "cover",
            }}
            priority
          />
        </div>
        {/* 右侧表单和说明 */}
        <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div style={{ width: "80%", maxWidth: "400px" }}>
            <div style={{ color: "#828282", fontSize: "16px", marginBottom: "18px", lineHeight: 1.7 }}>
              我们也不喜欢到处注册新账户（其实是开发账号管理系统有些复杂），目前仅需要ID即可登录个人的数据库——
              <b style={{ color: "#828282", textDecoration: "underline" }}>请一定要记好自己的ID！！</b>
            </div>
            <div style={{ fontWeight: "bold", fontSize: "17px", marginBottom: "18px" }}>
              输入你的专属ID：
            </div>
            <input
              type="text"
              placeholder="你的个人ID"
              onChange={e => setUserID(e.target.value)}
              style={{
                width: "100%",
                fontSize: "28px",
                padding: "14px 12px",
                borderRadius: "6px",
                border: "1px solid #ccc",
                marginBottom: "18px",
                background: "#f5f5f5",
                fontWeight: 500,
                outline: "none",
                boxSizing: "border-box",
              }}
            />
            <div style={{ color: "#888", fontSize: "15px", marginBottom: "18px" }}>
              {checkResult}
            </div>
            <Link href="/library" style={{ textDecoration: "none" }}> 
              <button
                style={{
                  width: "100%",
                  background: "#111",
                  color: "#fff",
                  border: "none",
                  borderRadius: "6px",
                  padding: "14px 0",
                  fontSize: "22px",
                  cursor: "pointer",
                  marginBottom: "24px",
                  marginTop: "6px",
                  letterSpacing: "2px",
                  transition: "background 0.2s",
                }}
              >
                登入！
              </button>
            </Link>
            <div style={{ color: "#888", fontSize: "13px", marginTop: "250px", lineHeight: 1.7 }}>
              小技巧：可以通过不同的ID来分开不同的使用需求，例如，<br />
              我有过“zuxxofEN01”和“zuxxofNovelS”来分别为我的资料和小说小小地建立云端的隔离库哦～
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}