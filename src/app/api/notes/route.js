const SERVER_URL = process.env.SERVER_URL?.trim().replace(/\/$/, "") || "http://localhost:5000";

export async function GET(req) {
    // 转发 GET 请求到 Flask 后端
    const url = SERVER_URL + "/api/notes" + (req.url.includes("?") ? req.url.slice(req.url.indexOf("?")) : "");
    const flaskRes = await fetch(url, { method: "GET" });
    const data = await flaskRes.json();
    return Response.json(data, { status: flaskRes.status });
}

export async function POST(req) {
    // 转发 POST 请求到 Flask 后端
    const body = await req.text();
    const flaskRes = await fetch(SERVER_URL + "/api/notes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body,
    });
    const data = await flaskRes.json();
    return Response.json(data, { status: flaskRes.status });
}

export async function DELETE(req) {
    // 转发 DELETE 请求到 Flask 后端
    const body = await req.text();
    const flaskRes = await fetch(SERVER_URL + "/api/notes", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body,
    });
    const data = await flaskRes.json();
    return Response.json(data, { status: flaskRes.status });
}