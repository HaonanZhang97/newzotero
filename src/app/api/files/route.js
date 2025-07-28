let files = [
    // 你可以预置一些测试数据
    {
        id: 0,
        title: "测试文档.pdf",
        meta: { title: "测试文档", author: "张三", date: "2025-07-27", page: "1-10", type: "pdf" },

    }
];

export async function GET() {
    return Response.json(files);
}

export async function POST(req) {
    const data = await req.json();
    files.push(data);
    return Response.json({ success: true });
}