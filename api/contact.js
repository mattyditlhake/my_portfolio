import { createTransport } from 'nodemailer';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ ok: false, error: 'Method not allowed' });
    return;
  }

  const { name, email, subject, message } = req.body || {};

  if (!name || !email || !subject || !message) {
    res.status(400).json({ ok: false, error: 'Please complete all required fields.' });
    return;
  }

  const transporter = createTransport({
    host: process.env.SMTP_HOST,
    port: Number(process.env.SMTP_PORT || 587),
    secure: false,
    auth: {
      user: process.env.SMTP_USER,
      pass: process.env.SMTP_PASS,
    },
  });

  try {
    await transporter.sendMail({
      from: process.env.SMTP_FROM || 'Portfolio Contact <no-reply@localhost>',
      to: process.env.RECEIVER_EMAIL || 'matty.ditlhake@gmail.com',
      replyTo: `${name} <${email}>`,
      subject: `Portfolio contact: ${subject}`,
      text: `Name: ${name}\nEmail: ${email}\n\nMessage:\n${message}`,
    });

    res.status(200).json({ ok: true });
  } catch (error) {
    console.error('Contact form error:', error);
    res.status(500).json({ ok: false, error: 'Unable to send message right now.' });
  }
}
