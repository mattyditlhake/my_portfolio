const { createTransport } = require('nodemailer');

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).send('Method not allowed');
    return;
  }

  const { name, email, subject, message } = req.body || {};

  if (!name || !email || !subject || !message) {
    res.status(400).send('Please complete all required fields.');
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

    res.status(200).send('OK');
  } catch (error) {
  console.error(error);

  res.status(500).json({
    message: error.message,
    stack: process.env.NODE_ENV !== "production" ? error.stack : undefined
  });
}
};
