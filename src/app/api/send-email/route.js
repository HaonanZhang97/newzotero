import nodemailer from 'nodemailer';

export async function POST(req) {
  try {
    const { email, context } = await req.json();

    const transporter = nodemailer.createTransport({
      host: process.env.EMAIL_HOST,
      port: Number(process.env.EMAIL_PORT),
      secure: Number(process.env.EMAIL_PORT) === 465, // true for 465, false for other ports
      auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS, // 和你的 .env 保持一致
      },
    });

    const mailOptions = {
      from: process.env.EMAIL_USER,
      to: process.env.EMAIL_RECIPIENT,
      subject: 'New Feedback from NewZotero ' + " ' "+ email + " ' ",
      text: context,
    };

    await transporter.sendMail(mailOptions);
    return Response.json({ success: true, message: '反馈已提交，我们将尽快回复您！' });
  } catch (error) {
    console.error('Error sending email:', error);
    return Response.json({ success: false, error: error.message }, { status: 500 });
  }
}