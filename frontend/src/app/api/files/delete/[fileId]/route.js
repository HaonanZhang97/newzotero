import { NextRequest, NextResponse } from 'next/server';

const SERVER_URL = process.env.SERVER_URL?.trim().replace(/\/$/, "") || "http://localhost:5000";

export async function DELETE(request, { params }) {
    try {
        const { fileId } = await params;
        const { searchParams } = new URL(request.url);
        const username = searchParams.get('username');

        if (!fileId) {
            return NextResponse.json(
                { success: false, error: '文件ID缺失' },
                { status: 400 }
            );
        }

        if (!username) {
            return NextResponse.json(
                { success: false, error: '用户名缺失' },
                { status: 400 }
            );
        }

        // 调用后端 Flask API 删除文件
        const backendResponse = await fetch(
            `${SERVER_URL}/api/files/delete/${fileId}?username=${encodeURIComponent(username)}`,
            {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
            }
        );

        if (!backendResponse.ok) {
            const error = await backendResponse.json();
            return NextResponse.json(
                { success: false, error: error.error || '删除失败' },
                { status: backendResponse.status }
            );
        }

        const result = await backendResponse.json();
        return NextResponse.json(result);

    } catch (error) {
        console.error('Delete API error:', error);
        return NextResponse.json(
            { success: false, error: '删除过程中发生错误' },
            { status: 500 }
        );
    }
}
