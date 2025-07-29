import { NextRequest, NextResponse } from 'next/server';

export async function GET(request, { params }) {
    try {
        const { fileId } = await params;
        const { searchParams } = new URL(request.url);
        const username = searchParams.get('username');

        if (!fileId || !username) {
            return NextResponse.json(
                { success: false, error: '文件ID或用户名缺失' },
                { status: 400 }
            );
        }

        // 调用后端 Flask API 下载文件
        const backendResponse = await fetch(
            `http://localhost:5000/api/download/${fileId}?username=${encodeURIComponent(username)}`,
            {
                method: 'GET',
            }
        );

        if (!backendResponse.ok) {
            const error = await backendResponse.json();
            return NextResponse.json(
                { success: false, error: error.error || '下载失败' },
                { status: backendResponse.status }
            );
        }

        // 获取文件内容和头部信息
        const fileBuffer = await backendResponse.arrayBuffer();
        const contentType = backendResponse.headers.get('content-type') || 'application/octet-stream';
        const contentDisposition = backendResponse.headers.get('content-disposition') || '';

        // 返回文件
        return new NextResponse(fileBuffer, {
            status: 200,
            headers: {
                'Content-Type': contentType,
                'Content-Disposition': contentDisposition,
            },
        });

    } catch (error) {
        console.error('Download API error:', error);
        return NextResponse.json(
            { success: false, error: '下载过程中发生错误' },
            { status: 500 }
        );
    }
}
