const SERVER_URL = process.env.SERVER_URL?.trim().replace(/\/$/, "") || "http://localhost:5000";

export async function POST(req) {
    // 直接转发 POST 请求到 Flask 后端
    const body = await req.text();
    const flaskRes = await fetch(SERVER_URL + "/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body,
    });
    const data = await flaskRes.json();
    return Response.json(data, { status: flaskRes.status });
}