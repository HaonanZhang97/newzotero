import { NextRequest, NextResponse } from 'next/server';

const SERVER_URL = process.env.SERVER_URL?.trim().replace(/\/$/, "") || "http://localhost:5000";

export async function POST(request) {
    try {
        const formData = await request.formData();
        const file = formData.get('file');
        const username = formData.get('username');

        if (!file || !username) {
            return NextResponse.json(
                { success: false, error: '文件或用户名缺失' },
                { status: 400 }
            );
        }

        // 创建新的 FormData 对象转发给后端
        const backendFormData = new FormData();
        backendFormData.append('file', file);
        backendFormData.append('username', username);

        // 调用后端 Flask API
        const backendResponse = await fetch(`${SERVER_URL}/api/upload`, {
            method: 'POST',
            body: backendFormData,
        });

        if (!backendResponse.ok) {
            const error = await backendResponse.json();
            return NextResponse.json(
                { success: false, error: error.error || '后端上传失败' },
                { status: backendResponse.status }
            );
        }

        const result = await backendResponse.json();
        return NextResponse.json(result);

    } catch (error) {
        console.error('Upload API error:', error);
        return NextResponse.json(
            { success: false, error: '上传过程中发生错误' },
            { status: 500 }
        );
    }
}
