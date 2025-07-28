export async function POST(request) {
    const { query, resultsPerPage } = await request.json();

    // 生成模拟数据
    const allResults = Array.from({ length: 20 }).map((_, i) => ({
        content: `这是笔记内容${i + 1}，和你的搜索“${query}”相关。`,
        title: `笔记标题${i + 1}`,
        author: `作者${String.fromCharCode(65 + (i % 5))}`,
        date: `2024-01-${String(i + 1).padStart(2, '0')}`,
        score: (Math.random() * 0.5).toFixed(2),
        type: i % 2 === 0 ? "abstract" : "free"
    }));

    let results;
    if (resultsPerPage === "all") {
        results = allResults;
    } else {
        results = allResults.slice(0, Number(resultsPerPage) || 5);
    }

    return Response.json({ results });
}