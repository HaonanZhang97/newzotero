let notes = [
    // 示例
    { id: 101, fileId: 0, content: "这是一个测试摘录", createdAt: "2025-07-27T12:00:00Z" },
    { id: 102, fileId: 0, content: "这是另一个测试摘录", createdAt: "2025-07-28T12:00:00Z" }
];

export async function GET(req) {
    // 支持按 fileId 查询
    const { searchParams } = new URL(req.url);
    const fileId = searchParams.get("fileId");
    if (fileId) {
        return Response.json(notes.filter(n => n.fileId == fileId));
    }
    return Response.json(notes);
}

export async function POST(req) {
    const data = await req.json();
    notes.push(data);
    return Response.json({ success: true });
}

export async function PUT(req) {
    const data = await req.json();
    notes = notes.map(n => n.id === data.id ? data : n);
    return Response.json({ success: true });
}

export async function DELETE(req) {
    const { id, fileId } = await req.json();
    if (fileId !== undefined) {
        notes = notes.filter(n => n.fileId !== fileId);
    } else if (id !== undefined) {
        notes = notes.filter(n => n.id !== id);
    }
    return Response.json({ success: true });
}