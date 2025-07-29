const SERVER_URL = process.env.SERVER_URL?.trim().replace(/\/$/, "") || "http://localhost:5000";

export async function POST(req) {
  try {
    // 读取前端传来的 form-data
    const formData = await req.formData();
    const body = new URLSearchParams();
    for (const [key, value] of formData.entries()) {
      body.append(key, value);
    }

    // 转发到 Flask 后端
    const flaskRes = await fetch(SERVER_URL + "/api/check_user", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: body.toString(),
    });

    const data = await flaskRes.json();
    return Response.json(data, { status: flaskRes.status });
  } catch (error) {
    return Response.json({ error: error.message }, { status: 500 });
  }
}